import logging
import os
import traceback

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.contrib.auth import update_session_auth_hash

from rest_framework import generics, status
from api.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib
import sklearn
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import UploadFile, Cow, Lactation, LactationData, MultiparousFeatures, Prediction, PrimiparousFeatures
from .serializers import LactationDataSerializer, MultiparousFeaturesSerializer, PrimiparousFeaturesSerializer, CurrentUserSerializer, ChangePasswordSerializer, ChangeEmailSerializer
from .processing.validate import validate
from .processing.clean import clean
from .processing.multi_features import multi_feature_construction
from .processing.primi_features import primi_feature_construction

matplotlib.use('Agg')
logger = logging.getLogger(__name__)

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] # Anyone can register


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            if not user.check_password(old_password):
                return Response({'old_password': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(generics.UpdateAPIView):
    serializer_class = ChangeEmailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            new_email = serializer.validated_data['email']
            user.email = new_email
            user.save()
            return Response({"message": "Email updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        user = request.user
        confirm = request.data.get('confirm', False)

        if not confirm:
            return Response({'detail': 'Account deletion not confirmed.'}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({'message': 'Account deleted successfully.'}, status=status.HTTP_200_OK)


class DataUploadView(APIView):
    parser_classes = [MultiPartParser]  # To handle file uploads
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated

    # def send_progress_message(self, user_id, message):
    #     try:
    #         channel_layer = get_channel_layer()
    #         # Create a unique group name for this user
    #         group_name = f"user_{user_id}_progress"
            
    #         # Send the message
    #         async_to_sync(channel_layer.group_send)(
    #             group_name,
    #             {
    #                 "type": "progress.message",  # This must match a method name in your consumer
    #                 "message": {
    #                     "progress": message
    #                 }
    #             }
    #         )
    #     except Exception as e:
    #         print(f"Error sending progress message: {str(e)}")
    
    def post(self, request, *args, **kwargs):
        logger.info("=== Starting File Upload ===")
        logger.info(f"User: {request.user.id}")
        logger.info(f"Files in request: {request.FILES}")
        logger.info(f"POST data: {request.POST}")
        
        try:
            # Send initial progress
            # self.send_progress_message(request.user.id, "Starting upload...")
            
            file_obj = request.FILES.get("file")
            if not file_obj:
                logger.error("No file provided in request")
                return Response({"message": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"File received: {file_obj.name} (size: {file_obj.size} bytes)")
            
            # Check user folder
            user_folder = os.path.join(settings.MEDIA_ROOT, f"uploads/user_{request.user.id}")
            file_path = os.path.join(user_folder, file_obj.name)
            logger.info(f"Target path: {file_path}")

            if os.path.exists(file_path):
                logger.warning(f"File already exists: {file_path}")
                return Response({
                    "message": "File already exists. Please rename the file."
                }, status=status.HTTP_409_CONFLICT)  

            # Save and load uploaded file
            try:
                logger.info("Saving uploaded file...")
                uploaded_file = UploadFile(user=request.user, file=file_obj)
                uploaded_file.save()
                file_path = uploaded_file.file.path
                logger.info(f"File saved to: {file_path}")
                
                logger.info("Reading CSV file...")
                data = pd.read_csv(file_path)
                logger.info(f"CSV loaded successfully. Shape: {data.shape}")

            except Exception as e:
                # self.send_progress_message(request.user.id, f"Error loading file: {str(e)}")
                logger.error(f"Error processing uploaded file: {str(e)}")
                logger.error(traceback.format_exc())
                return Response(
                    {"message": f"Error processing file: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Process uploaded file
            try:
                # self.send_progress_message(request.user.id, "Validating data...")
                logger.info("Starting data validation...")

                validated_data, eligible_lactations, validation_messages = validate(data)
                # for msg in validation_messages:
                #     self.send_progress_message(request.user.id, msg)
                logger.info(f"Validation complete. Messages: {validation_messages}")

                # self.send_progress_message(request.user.id, "Cleaning data...")
                logger.info("Starting data cleaning...")

                cleaned_data, cleaning_messages = clean(validated_data)
                # for msg in cleaning_messages:
                #     self.send_progress_message(request.user.id, msg)

                # self.send_progress_message(request.user.id, "Storing lactation data...")
                logger.info("Storing lactation data...")
                self.store_lactation_data(
                    cleaned_data, eligible_lactations, request.user
                )

                # self.send_progress_message(request.user.id, "Creating input features...")
                logger.info("Creating input features...")
                self.create_input_features(
                    eligible_lactations, cleaned_data, request.user
                )

                # self.send_progress_message(request.user.id, "Making predictions...")
                logger.info("Making predictions...")
                self.make_prediction(eligible_lactations, request)

                # self.send_progress_message(request.user.id, "Processing complete!")

            except ValueError as e:
                error_traceback = traceback.format_exc()
                logger.error(f"Error in data processing: {str(e)}")
                logger.error(error_traceback)
                return Response(
                    {"message": f"Error processing file: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            logger.info("=== File Processing Complete ===")
            return Response({
                "message": "File processed and data stored successfully! Predictions have been made!",
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error("=== Unexpected Error ===")
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return Response(
                {"message": f"Unexpected error: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
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
                # self.send_progress_message(
                #     user.id, 
                #     f"Warning: No data found for Cow {cow_id}, Parity {parity}. Skipping..."
                # )
                continue

            # Process and store each row in the subset
            for _, row in subset.iterrows():
                cow, _ = Cow.objects.get_or_create(cow_id=row['Cow'], owner=user)

                lactation, _ = Lactation.objects.get_or_create(
                    cow=cow, parity=row['Parity'], 
                    parity_type=Lactation.PRIMIPAROUS if row['Parity'] == 1 else Lactation.MULTIPAROUS
                )
                
                try:
                    LactationData.objects.get_or_create(
                        lactation=lactation,
                        dim=row['DIM'],
                        defaults={
                            'date': row['Date'],
                            'milk_yield': row['MilkTotal']
                        }
                    )

                except LactationData.DoesNotExist:
                    print(f"LactationData not found for Lactation {lactation} and DIM {row['DIM']}")
                    continue

    def create_input_features(self, eligible_lactations: list, cleaned_data: pd.DataFrame, user):
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
                    # self.send_progress_message(
                    #     user_id=user.id,
                    #     message=f"No data for current lactation of Cow {cow_id}, Parity {parity}. Skipping..."
                    # )
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
                    # self.send_progress_message(
                    #     user_id=user.id,
                    #     message=f"No data for current lactation of Cow {cow_id}, Parity {parity}. Skipping..."
                    # )
                    continue

                features = primi_feature_construction(current_lactation)


            if features.empty:
                # self.send_progress_message(
                #     user_id=user.id,
                #     message=f"Error creating features for Cow {cow_id} and Parity {parity}. Skipping..."
                # )
                continue

            try:
                lactation = Lactation.objects.filter(
                    cow__cow_id=cow_id, parity=parity, cow__owner=user
                    ).first()
                
            except Lactation.DoesNotExist:
                # self.send_progress_message(
                #     user_id=user.id,
                #     message=f"Lactation for Cow {cow_id} and Parity {parity} not found. Skipping..."
                # )
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
            'month_sin': features_df['month_sin'].iloc[0],
            'month_cos': features_df['month_cos'].iloc[0],
            'prev_a': features_df['prev_a'].iloc[0],  # Added
            'prev_305_my': features_df['prev_305_my'].iloc[0],
            'prev_lact_length': features_df['prev_lact_length'].iloc[0],  # Updated to match model
            'prev_my_end': features_df['prev_my_end'].iloc[0],  # Added
            'prev_days_to_peak': features_df['prev_days_to_peak'].iloc[0],
            'prev_peak_my': features_df['prev_peak_my'].iloc[0],  # Added
            'prev_persistency': features_df['prev_persistency'].iloc[0],
            'current_a': features_df['current_a'].iloc[0],  # Added
            'predicted_305_my': features_df['predicted_305_my'].iloc[0],
            'current_days_to_peak': features_df['current_days_to_peak'].iloc[0],  # Added
            'current_peak_my': features_df['current_peak_my'].iloc[0],  # Added
            'predicted_persistency': features_df['predicted_persistency'].iloc[0],  # Added
            'my_variance': features_df['my_variance'].iloc[0],  # Added
            'rate_of_my_change': features_df['rate_of_my_change'].iloc[0],  # Added
            'prev_dijkstra_b_eqn': features_df['prev_dijkstra_b_eqn'].iloc[0],  # Added
            'prev_dijkstra_b0_eqn': features_df['prev_dijkstra_b0_eqn'].iloc[0],  # Added
            'prev_dijkstra_c_eqn': features_df['prev_dijkstra_c_eqn'].iloc[0],  # Added
            'current_dijkstra_b_eqn': features_df['current_dijkstra_b_eqn'].iloc[0],  # Added
            'current_dijkstra_b0_eqn': features_df['current_dijkstra_b0_eqn'].iloc[0],  # Added
            'current_dijkstra_c_eqn': features_df['current_dijkstra_c_eqn'].iloc[0],  # Added
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
                    'month_sin': features_df['month_sin'].iloc[0],
                    'month_cos': features_df['month_cos'].iloc[0],
                    'a' : features_df['a'].iloc[0],
                    'my_variance': features_df['my_variance'].iloc[0],  # Added
                    'rate_of_my_change': features_df['rate_of_my_change'].iloc[0],  # Added
                    'predicted_305_my': features_df['predicted_305_my'].iloc[0],
                    'current_dijkstra_b_eqn': features_df['current_dijkstra_b_eqn'].iloc[0],  # Added
                    'current_dijkstra_b_b0_eqn': features_df['current_dijkstra_b_b0_eqn'].iloc[0],  # Added
                    'current_dijkstra_b0_eqn': features_df['current_dijkstra_b0_eqn'].iloc[0],  # Added
                    'current_dijkstra_c_eqn': features_df['current_dijkstra_c_eqn'].iloc[0],  # Added
                }
            )

        if created:
            print(f"Created new features for lactation {lactation}")
        else:
            print(f"Updated features for lactation {lactation}")

    def load_model(self, parity_type):
        models_dir = os.path.join(settings.BASE_DIR, "api/ml_models")
        if parity_type == Lactation.PRIMIPAROUS:
            model_path = os.path.join(models_dir, "primi_svr.pkl")
        elif parity_type == Lactation.MULTIPAROUS:
            model_path = os.path.join(models_dir, "multi_voting_ensemble.pkl")
        else:
            raise ValueError(
                f"load_models got an unexpected parity type: {parity_type}"
                )
        return joblib.load(model_path)

    def get_input_features(self, lactation, parity):
        """Gets the input features for a given lactation and parity."""
        
        def fetch_features(model, lactation, feature_list):
            """Helper function to fetch features and handle exceptions."""
            try:
                features = model.objects.get(lactation=lactation)
                feature_values = [
                    getattr(features, feature) for feature in feature_list
                    ]
                return np.array(feature_values).reshape(1, -1)
                       
            except model.DoesNotExist:
                print(f"No features found for Lactation {lactation}. Skipping...")
                return None
        
        if parity > 1:
            # Multiparous feature list
            multiparous_feature_list = [
                'parity', 'milk_total_1_10', 'milk_total_11_20', 'milk_total_21_30', 
                'milk_total_31_40', 'milk_total_41_50', 'milk_total_51_60', 'month_sin', 
                'month_cos', 'prev_a', 'prev_305_my', 'prev_lact_length', 'prev_my_end', 
                'prev_days_to_peak', 'prev_peak_my', 'prev_persistency', 'current_a', 
                'predicted_305_my', 'current_days_to_peak', 'current_peak_my', 
                'predicted_persistency', 'my_variance', 'rate_of_my_change', 
                'prev_dijkstra_b_eqn', 'prev_dijkstra_b0_eqn', 'prev_dijkstra_c_eqn', 
                'current_dijkstra_b_eqn', 'current_dijkstra_b0_eqn', 'current_dijkstra_c_eqn'
            ]
            return fetch_features(MultiparousFeatures, lactation, multiparous_feature_list)

        elif parity == 1:
            # Primiparous feature list
            primiparous_feature_list = [
                'milk_total_1_10',
                'milk_total_11_20',
                'milk_total_21_30',
                'milk_total_31_40',
                'milk_total_41_50',
                'milk_total_51_60',
                'month_sin',
                'month_cos',
                'a',
                'my_variance',
                'rate_of_my_change',
                'predicted_305_my',
                'current_dijkstra_b_eqn',
                'current_dijkstra_b_b0_eqn',
                'current_dijkstra_b0_eqn',
                'current_dijkstra_c_eqn',
            ]
            return fetch_features(PrimiparousFeatures, lactation, primiparous_feature_list)
        
        return None

    def store_prediction(self, lactation, prediction, extrapolations):
        """
        Store the prediction in the database.

        Args:
            lactation: The Lactation object for which the prediction is made.
            prediction: The predicted value.
        """
        Prediction.objects.create(
            lactation=lactation,
            prediction_type='regression',
            prediction_value=prediction,
            approximate_persistency=extrapolations["approx_persistency"],
            extend_1_cycle=extrapolations["extend_1_cycle"],
            extend_2_cycle=extrapolations["extend_2_cycle"],
            extend_3_cycle=extrapolations["extend_3_cycle"],
            days_to_target=extrapolations["days_to_target"],
            plot_path=extrapolations["plot_path"],
        )

    def make_prediction(self, eligible_lactations, request):
        """
        Iterate over eligible lactations, load the correct model, retrieve the input features, 
        make the prediction, and store the result.

        Args:
            eligible_lactations: List of (Cow ID, Parity) tuples for eligible lactations.
        """
        for cow_id, parity in eligible_lactations:
            try:
                lactation = Lactation.objects.filter(
                    cow__cow_id=cow_id, parity=parity, cow__owner=request.user
                    ).first()
                model = self.load_model(lactation.parity_type)
                input_features = self.get_input_features(lactation, parity)

                if input_features is None:
                    continue
                
                prediction = model.predict(input_features)[0]
                extrapolations = self.make_extrapolation(
                    prediction, lactation, request
                    )
                self.store_prediction(lactation, prediction, extrapolations)

            except Lactation.DoesNotExist:
                print(f"Lactation for Cow {cow_id}, Parity {parity} not found.")
                continue

    def make_extrapolation(self, predicted_305_my, lactation, request):
        
        def predict_cycle_my(day_305_my, persistency, num_cycles):
            return day_305_my + (persistency * (21 * num_cycles))

        def predict_days_to_target(day_305_my, persistency):
            if day_305_my > 25:
                return 305 + int((25 - day_305_my) / persistency)
            else:
                return 0

        def plot_days_to_target(lactation_data, predicted_305_my, approx_persistency, last_dim, days_to_target, cow_id, parity, request):
            """
            Creates and saves a plot showing Milk Yield vs DIM, along with predictions.
            
            Args:
                lactation_data (QuerySet): Lactation data for the first 60 DIM.
                predicted_305_my (float): Predicted milk yield at day 305.
                approx_persistency (float): The approximate persistency.
                last_dim (int): The last DIM recorded for the lactation.
                days_to_target (float): The DIM at which milk yield is expected to reach 25 kg/d.
                cow_id (str): The cow ID.
                parity (int): The lactation parity.
            
            Returns:
                str: The path to the saved plot image.
            """
            dims = [entry.dim for entry in lactation_data]
            milk_yields = [entry.milk_yield for entry in lactation_data]

            # Create the plot
            plt.figure(figsize=(10, 6))
            plt.plot(dims, milk_yields, label="Milk Yield (first 60 DIM)", marker='o')

            # Vertical lines at DIM 60 and 305
            plt.axvline(x=60, color='blue', linestyle='--', label='DIM 60')
            plt.axvline(x=305, color='orange', linestyle='--', label='DIM 305')

            # Predicted day 305 MY
            plt.scatter([305], [predicted_305_my], color='red', label=f"Predicted 305 MY: {predicted_305_my:.2f} kg", zorder=5)

            # Dashed line for persistency
            plt.plot([last_dim, 305], [milk_yields[-1], predicted_305_my], 'r--', label=f"Persistency (from DIM {last_dim})")

            # Annotate the slope of the persistency line
            slope = approx_persistency
            mid_dim = (last_dim + 305) / 2
            mid_milk_yield = (milk_yields[-1] + predicted_305_my) / 2
            plt.text(mid_dim, mid_milk_yield, f"Slope: {slope:.2f}", color='red', fontsize=10)

            # Plot days to 20kg/d target
            plt.scatter([days_to_target], [25], color='green', label=f"Days to 25 kg/d: {days_to_target:.0f} DIM", zorder=5)

            # Labels and legend
            plt.xlabel("DIM (Days In Milk)")
            plt.ylabel("Milk Yield (kg/d)")
            plt.title(f"Milk Yield and Persistency Extrapolation for Cow {cow_id}, Parity {parity}")
            plt.legend(loc="upper right")

            # Save the plot to a file
            plot_filename = f"lactation_plot_cow_{cow_id}_parity_{parity}.png"
            plot_dir = os.path.join(settings.MEDIA_ROOT, f"extrapolation_plots/user_{request.user.id}")
            os.makedirs(plot_dir, exist_ok=True)
            plot_path = os.path.join(plot_dir, plot_filename)
            plt.tight_layout()
            plt.savefig(plot_path)
            plt.close()

            return os.path.join(f"extrapolation_plots/user_{request.user.id}", plot_filename)

        lactation_data = LactationData.objects.filter(lactation=lactation, dim__lte=60).order_by("dim")
        
        if lactation_data.exists():
            # Approximate persistency
            dim_56_to_60 = lactation_data.filter(dim__gte=56, dim__lte=60)
            last_milk_yield = dim_56_to_60.aggregate(avg_yield=Avg('milk_yield'))['avg_yield']
            # last_milk_yield = lactation_data.last().milk_yield
            # last_dim = lactation_data.last().dim
            approx_persistency = (predicted_305_my - last_milk_yield) / (305 - 60)
           
            # Predict MY after extending by n cycles
            extend_1_cycle = predict_cycle_my(
                predicted_305_my, approx_persistency, 1
                )
            extend_2_cycle = predict_cycle_my(
                predicted_305_my, approx_persistency, 2
                )
            extend_3_cycle = predict_cycle_my(
                predicted_305_my, approx_persistency, 3
                )
            
            # Predict days to 20kg/d target
            days_to_target = predict_days_to_target(
                predicted_305_my, approx_persistency
                )
            
            plot_path = plot_days_to_target(
                lactation_data=lactation_data,
                predicted_305_my=predicted_305_my,
                approx_persistency=approx_persistency,
                last_dim=60,
                days_to_target=days_to_target,
                cow_id=lactation.cow.cow_id,
                parity=lactation.parity,
                request=request
            )

            return {
                "approx_persistency": approx_persistency,
                "extend_1_cycle": extend_1_cycle,
                "extend_2_cycle": extend_2_cycle,
                "extend_3_cycle": extend_3_cycle,
                "days_to_target": days_to_target,
                "plot_path": plot_path
            }
        
        else:
            print(f"No lactation data found for Cow {lactation.cow.cow_id}, Parity {lactation.parity}.")
            return None, None
        

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
        predictions = Prediction.objects.filter(lactation__cow__owner=request.user).select_related("lactation__cow")
        base_url = os.getenv('BACKEND_URL')
        if not base_url.startswith(('http://', 'https://')):
            base_url = f"https://{base_url}"
        
        if not predictions.exists():
            logging.info("No predictions found")

        data = []
        for prediction in predictions:

            plot_url = None
            if prediction.plot_path:
                clean_path = prediction.plot_path.lstrip('/')
                plot_url = f"{base_url}/media/{clean_path}"
                logging.info(f"Generated plot URL: {plot_url}")

            data.append({
                "cow_id": prediction.lactation.cow.cow_id,
                "parity": prediction.lactation.parity,
                "predicted_value": prediction.prediction_value,
                "lactation_id": prediction.lactation.id,
                "treatment_group": prediction.lactation.treatment_group,
                "plot_path": plot_url,
                "extend_1_cycle": prediction.extend_1_cycle,
                "extend_2_cycle": prediction.extend_2_cycle,
                "extend_3_cycle": prediction.extend_3_cycle,
                "days_to_target": prediction.days_to_target,
            })
        logging.info(f"Returning {len(data)} predictions")
        return Response(data, status=status.HTTP_200_OK)
    

class TreatmentListView(APIView):
    def get(self, request):
        lactations = Lactation.objects.filter(cow__owner=request.user).select_related('cow')
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
        

class LactationDataListView(generics.ListAPIView):
    serializer_class = LactationDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = LactationData.objects.filter(
            lactation__cow__owner=self.request.user
        )
        cow_id = self.request.query_params.get('cow_id', None)
        parity = self.request.query_params.get('parity', None)

        if cow_id:
            queryset = queryset.filter(lactation__cow__cow_id=cow_id)
        if parity:
            queryset = queryset.filter(lactation__parity=parity)

        return queryset

class MultiparousFeaturesListView(generics.ListAPIView):
    serializer_class = MultiparousFeaturesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = MultiparousFeatures.objects.filter(
            lactation__cow__owner=self.request.user
        )
        cow_id = self.request.query_params.get('cow_id', None)
        parity = self.request.query_params.get('parity', None)

        if cow_id:
            queryset = queryset.filter(lactation__cow__cow_id=cow_id)
        if parity:
            queryset = queryset.filter(lactation__parity=parity)

        return queryset

class PrimiparousFeaturesListView(generics.ListAPIView):
    serializer_class = PrimiparousFeaturesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = PrimiparousFeatures.objects.filter(
            lactation__cow__owner=self.request.user
        )
        cow_id = self.request.query_params.get('cow_id', None)
        parity = self.request.query_params.get('parity', None)

        if cow_id:
            queryset = queryset.filter(lactation__cow__cow_id=cow_id)
        if parity:
            queryset = queryset.filter(lactation__parity=parity)

        return queryset