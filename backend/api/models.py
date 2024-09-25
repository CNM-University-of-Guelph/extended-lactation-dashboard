from django.db import models
from django.contrib.auth.models import User

class UploadFile(models.Model):
    file = models.FileField(upload_to="uploads/")   # Store files in a folder called uploads
    upload_time = models.DateTimeField(auto_now_add=True)
    