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

    TREATMENT_GROUP_CHOICES = [
        ('No group', 'No Group'),
        ('Extend 1 cycle', 'Extend 1 cycle'),
        ('Extend 2 cycles', 'Extend 2 cycles'),
        ('Extend 3 cycles', 'Extend 3 cycles'),
        ('Extend 4 cycles', 'Extend 4 cycles'),
        ('Extend 5 cycles', 'Extend 5 cycles'),
        ('Extend 6 cycles', 'Extend 6 cycles'),
        ('Extend 7 cycles', 'Extend 7 cycles'),
        ('Extend 8 cycles', 'Extend 8 cycles'),
        ('Extend 9 cycles', 'Extend 9 cycles'),
        ('Extend 10 cycles', 'Extend 10 cycles'),
        ('Do not extend', 'Do not extend')
    ]

    cow = models.ForeignKey(Cow, on_delete=models.CASCADE)
    parity = models.IntegerField()
    parity_type = models.CharField(max_length=15, choices=PARITY_TYPE_CHOICES)
    treatment_group = models.CharField(
        max_length=20,
        choices=TREATMENT_GROUP_CHOICES,
        default='No group'
    ) 

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
    

class MultiparousFeatures(models.Model):
    lactation = models.OneToOneField(Lactation, on_delete=models.CASCADE)
    parity = models.FloatField()  # Parity of the cow
    milk_total_1_10 = models.FloatField()  # Milk total for days 1-10
    milk_total_11_20 = models.FloatField()  # Milk total for days 11-20
    milk_total_21_30 = models.FloatField()  # Milk total for days 21-30
    milk_total_31_40 = models.FloatField()  # Milk total for days 31-40
    milk_total_41_50 = models.FloatField()  # Milk total for days 41-50
    milk_total_51_60 = models.FloatField()  # Milk total for days 51-60
    month_sin = models.FloatField()  # Sine of month
    month_cos = models.FloatField()  # Cosine of month
    prev_a = models.FloatField()  # Dijkstra a parameter
    prev_305_my = models.FloatField()  # 305-day milk yield in previous lactation
    prev_lact_length = models.FloatField()  # Length of the previous lactation
    prev_my_end = models.FloatField()  # Previous milk yield at end
    prev_days_to_peak = models.FloatField()  # Days to peak milk production in previous lactation
    prev_peak_my = models.FloatField()  # Previous peak milk yield
    prev_persistency = models.FloatField()  # Persistency of the previous lactation
    current_a = models.FloatField()  # Current Dijkstra a parameter
    predicted_305_my = models.FloatField()  # Predicted 305-day milk yield in current lactation  
    current_days_to_peak = models.FloatField()  # Current days to peak milk production
    current_peak_my = models.FloatField()  # Current peak milk yield
    predicted_persistency = models.FloatField()  # Predicted persistency
    my_variance = models.FloatField()  # Variance of milk total
    rate_of_my_change = models.FloatField()  # Rate of change in milk total
    prev_dijkstra_b_eqn = models.FloatField()  # Previous Dijkstra b equation parameter
    prev_dijkstra_b0_eqn = models.FloatField()  # Previous Dijkstra b0 equation parameter
    prev_dijkstra_c_eqn = models.FloatField()  # Previous Dijkstra c equation parameter
    current_dijkstra_b_eqn = models.FloatField()  # Current Dijkstra b equation parameter
    current_dijkstra_b0_eqn = models.FloatField()  # Current Dijkstra b0 equation parameter
    current_dijkstra_c_eqn = models.FloatField()  # Current Dijkstra c equation parameter

    def __str__(self):
        return f"Features for {self.lactation.cow.cow_id} - Parity {self.lactation.parity}"


class PrimiparousFeatures(models.Model):
    lactation = models.OneToOneField(Lactation, on_delete=models.CASCADE)
    milk_total_1_10 = models.FloatField()  # Milk total for days 1-10
    milk_total_11_20 = models.FloatField()  # Milk total for days 11-20
    milk_total_21_30 = models.FloatField()  # Milk total for days 21-30
    milk_total_31_40 = models.FloatField()  # Milk total for days 31-40
    milk_total_41_50 = models.FloatField()  # Milk total for days 41-50
    milk_total_51_60 = models.FloatField()  # Milk total for days 51-60
    month_sin = models.FloatField()  # Sine of month
    month_cos = models.FloatField()  # Cosine of month
    a = models.FloatField() # Dijkstra a parameter
    my_variance = models.FloatField()  # Variance of milk total
    rate_of_my_change = models.FloatField()  # Rate of change in milk total
    predicted_305_my = models.FloatField()  # Predicted 305-day milk yield in current lactation  
    current_dijkstra_b_eqn = models.FloatField()  # Current Dijkstra b equation parameter
    current_dijkstra_b_b0_eqn = models.FloatField()  # Current Dijkstra b b0 equation parameter
    current_dijkstra_b0_eqn = models.FloatField()  # Current Dijkstra b0 equation parameter
    current_dijkstra_c_eqn = models.FloatField()  # Current Dijkstra c equation parameter

    def __str__(self):
        return f"Features for {self.lactation.cow.cow_id} - Parity {self.lactation.parity}"
    

class Prediction(models.Model):
    lactation = models.ForeignKey(Lactation, on_delete=models.CASCADE)
    prediction_type = models.CharField(max_length=50, default="regression")
    prediction_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    approximate_persistency = models.FloatField()
    extend_1_cycle = models.FloatField(default=0)
    extend_2_cycle = models.FloatField(default=0)
    extend_3_cycle = models.FloatField(default=0)
    extend_4_cycle = models.FloatField(default=0)
    extend_5_cycle = models.FloatField(default=0)
    extend_6_cycle = models.FloatField(default=0)
    extend_7_cycle = models.FloatField(default=0)
    extend_8_cycle = models.FloatField(default=0)
    extend_9_cycle = models.FloatField(default=0)
    extend_10_cycle = models.FloatField(default=0)
    days_to_target = models.IntegerField()
    plot_path = models.CharField(max_length=255)

    class Meta:
        unique_together = ("lactation", "prediction_type")

    def __str__(self):
        return f"Prediction for {self.lactation.cow.cow_id} - Parity {self.lactation.parity}"
    

class DatabaseExport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Database Export for {self.user.username} on {self.created_at}"
    