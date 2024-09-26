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

from .models import UploadFile

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

        try:
            # Save the file on the server
            uploaded_file = UploadFile(user=request.user, file=file_obj)
            uploaded_file.save()
            
            # Process uploaded data
            file_path = uploaded_file.file.path

            data = pd.read_csv(file_path)
            data["New Column"] = data["Milk Yield"] * data["DIM"]

            processed_file_path = file_path.replace(".csv", "_processed.csv")
            data.to_csv(processed_file_path, index=False)

            return Response({
                "message": "File processed successfully!",
                "processed_file": processed_file_path
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"Error processing file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        