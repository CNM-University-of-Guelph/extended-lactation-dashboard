from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    return f"uploads/user_{instance.user.id}/{filename}"

class UploadFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)   # Store files in a folder called uploads
    upload_time = models.DateTimeField(auto_now_add=True)
    
class Cow(models.Model):
    cow_id = models.CharField(max_length=20)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["cow_id", "owner"]

    def __str__(self):
        return f"Cow {self.cow_id}"
    

class Lactation(models.Model):
    PRIMIPAROUS = "primiparous"
    MULTIPAROUS = "multiparous"

    PARITY_TYPE_CHOICES = [
        (PRIMIPAROUS, "Primiparous"),
        (MULTIPAROUS, "Multiparous")
    ]

    cow = models.ForeignKey(Cow, on_delete=models.CASCADE)
    parity = models.IntegerField()
    parity_type = models.CharField(max_length=15, choices=PARITY_TYPE_CHOICES)

    def __str__(self):
        return f"Cow {self.cow.cow_id} - Parity {self.parity}"


class LactationData(models.Model):
    lactation = models.ForeignKey(Lactation, on_delete=models.CASCADE)
    dim = models.IntegerField()
    date = models.DateField()
    milk_yield = models.FloatField()

    class Meta:
        unique_together = ["lactation", "dim"]
    
    def __str__(self):
        return f"Lactation {self.lactation} - DIM {self.dim}"
    