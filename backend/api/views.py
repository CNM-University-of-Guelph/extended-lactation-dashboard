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

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"message": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the file on the server
        uploaded_file = UploadFile.objects.create(file=file_obj)

        # Process uploaded data
        file_path = uploaded_file.file.path
        try:
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
        