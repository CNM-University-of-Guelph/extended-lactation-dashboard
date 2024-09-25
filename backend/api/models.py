from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    return f"uploads/user_{instance.user.id}/{filename}"

class UploadFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)   # Store files in a folder called uploads
    upload_time = models.DateTimeField(auto_now_add=True)
    