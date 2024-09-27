import os

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, status
from api.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
import pandas as pd

from .models import UploadFile, Cow, Lactation, LactationData
from .processing.validate import validate
from .processing.clean import clean

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

        except ValueError as e:
            return Response({"message": f"Error processing file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "File processed and data stored successfully!",
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
        