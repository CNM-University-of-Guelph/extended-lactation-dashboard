import logging
import os

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from api.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
import numpy as np
import pandas as pd
import joblib

from .models import UploadFile, Cow, Lactation, LactationData, MultiparousFeatures, Prediction, PrimiparousFeatures
from .processing.validate import validate
from .processing.clean import clean
from .processing.multi_features import multi_feature_construction
from .processing.primi_features import primi_feature_construction

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] # Anyone can register


class DataUploadView(APIView):
    parser_classes = [MultiPartParser]  # To handle file uploads
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"message": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        user_folder = os.path.join(settings.MEDIA_ROOT, f"uploads/user_{request.user.id}")
        file_path = os.path.join(user_folder, file_obj.name)

        if os.path.exists(file_path):
            return Response({
                "message": "File already exists. Please rename the file."
            }, status=status.HTTP_409_CONFLICT)  

        # Save and load uploaded file
        try:
            uploaded_file = UploadFile(user=request.user, file=file_obj)
            uploaded_file.save()
            file_path = uploaded_file.file.path
            data = pd.read_csv(file_path)

        except Exception as e:
            return Response(
                {"message": f"Error processing file: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Process uploaded file
        try:
            validated_data, eligible_lactations = validate(data)
            cleaned_data = clean(validated_data)
            
            self.store_lactation_data(
                cleaned_data, eligible_lactations, request.user
            )

            self.create_input_features(
                eligible_lactations, cleaned_data
            )

            self.make_prediction(eligible_lactations)

        except ValueError as e:
            return Response({"message": f"Error processing file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "File processed and data stored successfully! Predictions have been made!",
        }, status=status.HTTP_200_OK)
    
    def store_lactation_data(
        self, 
        cleaned_data: pd.DataFrame, 
        eligible_lactations: list, 
        user
    ):
        """Store lactation data for eligible cows and their current and previous lactations.
        
        Args:
            cleaned_data (pd.DataFrame): The full cleaned dataset.
            eligible_lactations (list): List of tuples containing (Cow ID, Parity) for eligible lactations.
            user: The user uploading the data.
        """
        for cow_id, parity in eligible_lactations:
            subset = cleaned_data[(cleaned_data['Cow'] == cow_id) & 
                                (cleaned_data['Parity'].isin([parity, parity - 1]))]
            
            if subset.empty:
                continue

            # Process and store each row in the subset
            for _, row in subset.iterrows():
                cow, _ = Cow.objects.get_or_create(cow_id=row['Cow'], owner=user)

                lactation, _ = Lactation.objects.get_or_create(
                    cow=cow, parity=row['Parity'], 
                    parity_type=Lactation.PRIMIPAROUS if row['Parity'] == 1 else Lactation.MULTIPAROUS
                )

                LactationData.objects.get_or_create(
                    lactation=lactation,
                    dim=row['DIM'],
                    defaults={
                        'date': row['Date'],
                        'milk_yield': row['MilkTotal']
                    }
                )

    def create_input_features(self, eligible_lactations: list, cleaned_data: pd.DataFrame):
        for cow_id, parity in eligible_lactations:
            if parity > 1:
                current_lactation = cleaned_data[
                    (cleaned_data['Cow'] == cow_id) & (cleaned_data['Parity'] == parity)
                    ]
        
                previous_lactation = cleaned_data[
                    (cleaned_data['Cow'] == cow_id) & (cleaned_data['Parity'] == parity - 1)
                    ]
        
                # Skip if no current lactation data exists
                if current_lactation.empty:
                    print(f"No data for current lactation of Cow {cow_id}, Parity {parity}")
                    continue

                features = multi_feature_construction(
                    current_lactation, previous_lactation
                    )
            
            elif parity == 1:
                current_lactation = cleaned_data[
                    (cleaned_data['Cow'] == cow_id) & (cleaned_data['Parity'] == parity)
                    ]
                
                # Skip if no current lactation data exists
                if current_lactation.empty:
                    print(f"No data for current lactation of Cow {cow_id}, Parity {parity}")
                    continue

                features = primi_feature_construction(current_lactation)


            if features.empty:
                print(f"Features for Cow {cow_id} and Parity {parity} is empty.")
                continue

            try:
                lactation = Lactation.objects.get(
                    cow__cow_id=cow_id, parity=parity
                    )
                
            except Lactation.DoesNotExist:
                print(f"Lactation for Cow {cow_id} and Parity {parity} not found.")
                continue
            
            self.store_features(lactation, parity, features)
            
    def store_features(self, lactation, parity, features_df: pd.DataFrame):
        """
        Store the multiparous features for a given lactation.

        Args:
            lactation: The Lactation object.
            features_df: A DataFrame containing the calculated features.
        """
        if parity > 1:
            features, created = MultiparousFeatures.objects.update_or_create(
                lactation=lactation,
                defaults={
                    'parity': features_df['Parity'].iloc[0],
                    'milk_total_1_10': features_df['MilkTotal_1-10'].iloc[0],
                    'milk_total_11_20': features_df['MilkTotal_11-20'].iloc[0],
                    'milk_total_21_30': features_df['MilkTotal_21-30'].iloc[0],
                    'milk_total_31_40': features_df['MilkTotal_31-40'].iloc[0],
                    'milk_total_41_50': features_df['MilkTotal_41-50'].iloc[0],
                    'milk_total_51_60': features_df['MilkTotal_51-60'].iloc[0],
                    'month_sin': features_df['Month_sin'].iloc[0],
                    'month_cos': features_df['Month_cos'].iloc[0],
                    'prev_persistency': features_df['prev_persistency'].iloc[0],
                    'prev_lactation_length': features_df['prev_lactation_length'].iloc[0],
                    'prev_days_to_peak': features_df['prev_days_to_peak'].iloc[0],
                    'prev_305_my': features_df['prev_305_my'].iloc[0],
                    'persistency': features_df['persistency'].iloc[0],
                    'days_to_peak': features_df['days_to_peak'].iloc[0],
                    'predicted_305_my': features_df['predicted_305_my'].iloc[0],
                }
            )
            
        elif parity == 1:
            features, created = PrimiparousFeatures.objects.update_or_create(
                lactation=lactation,
                defaults={
                    'milk_total_1_10': features_df['MilkTotal_1-10'].iloc[0],
                    'milk_total_11_20': features_df['MilkTotal_11-20'].iloc[0],
                    'milk_total_21_30': features_df['MilkTotal_21-30'].iloc[0],
                    'milk_total_31_40': features_df['MilkTotal_31-40'].iloc[0],
                    'milk_total_41_50': features_df['MilkTotal_41-50'].iloc[0],
                    'milk_total_51_60': features_df['MilkTotal_51-60'].iloc[0],
                    'predicted_305_my': features_df['predicted_305_my'].iloc[0],
                    'a' : features_df['a'].iloc[0],
                    'b' : features_df['b'].iloc[0],
                    'b0' : features_df['b0'].iloc[0],
                    'c' : features_df['c'].iloc[0],
                    'month_sin': features_df['Month_sin'].iloc[0],
                    'month_cos': features_df['Month_cos'].iloc[0],
                }
            )

        if created:
            print(f"Created new features for lactation {lactation}")
        else:
            print(f"Updated features for lactation {lactation}")

    def load_model(self, parity_type):
        models_dir = os.path.join(settings.BASE_DIR, "api/ml_models")
        if parity_type == Lactation.PRIMIPAROUS:
            pass
        elif parity_type == Lactation.MULTIPAROUS:
            model_path = os.path.join(models_dir, "SVR_multiparous.sav")
        else:
            raise ValueError(
                f"load_models got an unexpected parity type: {parity_type}"
                )
        model = joblib.load(model_path)
        return model

    def get_input_features(self, lactation):
        try:
            features = MultiparousFeatures.objects.get(lactation=lactation)
            feature_values = [
                features.parity,
                features.milk_total_1_10,
                features.milk_total_11_20,
                features.milk_total_21_30,
                features.milk_total_31_40,
                features.milk_total_41_50,
                features.milk_total_51_60,
                features.prev_persistency,
                features.prev_lactation_length,
                features.prev_days_to_peak,
                features.prev_305_my,
                features.persistency,
                features.days_to_peak,
                features.predicted_305_my,
                features.month_sin,
                features.month_cos
            ]
            return np.array(feature_values).reshape(1, -1)

        except MultiparousFeatures.DoesNotExist:
            print(f"No features found for Lactation {lactation}. Skipping...")
            return None

    def store_prediction(slef, lactation, prediction):
        """
        Store the prediction in the database.

        Args:
            lactation: The Lactation object for which the prediction is made.
            prediction: The predicted value.
        """
        Prediction.objects.create(
            lactation=lactation,
            prediction_type='regression',
            prediction_value=prediction
        )

    def make_prediction(self, eligible_lactations):
        """
        Iterate over eligible lactations, load the correct model, retrieve the input features, 
        make the prediction, and store the result.

        Args:
            eligible_lactations: List of (Cow ID, Parity) tuples for eligible lactations.
        """
        for cow_id, parity in eligible_lactations:
            try:
                lactation = Lactation.objects.get(cow__cow_id=cow_id, parity=parity)
                model = self.load_model(lactation.parity_type)
                input_features = self.get_input_features(lactation)

                if input_features is None:
                    continue
                
                prediction = model.predict(input_features)[0]
                self.store_prediction(lactation, prediction)

            except Lactation.DoesNotExist:
                print(f"Lactation for Cow {cow_id}, Parity {parity} not found.")
                continue


class ListUserFilesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_folder = os.path.join(settings.MEDIA_ROOT, f"uploads/user_{request.user.id}")
        if os.path.exists(user_folder):
            files = [file for file in os.listdir(user_folder) if file.endswith(".csv")]
        else:
            files = []

        return Response({"files": files})
       

class GetUserFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, filename, *args, **kwargs):
        user_folder = os.path.join(settings.MEDIA_ROOT, f"uploads/user_{request.user.id}")
        file_path = os.path.join(user_folder, filename)
        if os.path.exists(file_path):
            return FileResponse(open(file_path, "rb"), content_type="text/csv")
        else:
            return Response({"message": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        

class PredictionsListView(APIView):
    def get(self, request):
        logging.info("Predictions API called")
        predictions = Prediction.objects.all().select_related("lactation__cow")

        if not predictions.exists():
            logging.info("No predictions found")

        data = []
        for prediction in predictions:
            data.append({
                "cow_id": prediction.lactation.cow.cow_id,
                "parity": prediction.lactation.parity,
                "predicted_value": prediction.prediction_value,
                "lactation_id": prediction.lactation.id,
                "treatment_group": prediction.lactation.treatment_group,
            })
        logging.info(f"Returning {len(data)} predictions")
        return Response(data, status=status.HTTP_200_OK)
    

class TreatmentListView(APIView):
    def get(self, request):
        lactations = Lactation.objects.all().select_related('cow')
        data = [
            {
                "cow_id": lactation.cow.cow_id,
                "parity": lactation.parity,
                "treatment_group": lactation.treatment_group
            }
            for lactation in lactations
        ]
        return Response(data, status=status.HTTP_200_OK)
        

class UpdateTreatmentGroupView(APIView):
    def post(self, request, lactation_id):
        try:
            lactation = get_object_or_404(Lactation, id=lactation_id)
            new_treatment_group = request.data.get('treatment_group')  # Use request.data for JSON payloads

            if new_treatment_group in dict(Lactation.TREATMENT_GROUP_CHOICES).keys():
                lactation.treatment_group = new_treatment_group
                lactation.save()
                return Response({
                    "status": "success",
                    "message": f"Treatment group updated to {new_treatment_group}"
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "error",
                    "message": "Invalid treatment group value"
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        