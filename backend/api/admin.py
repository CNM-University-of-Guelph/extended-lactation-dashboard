from django.contrib import admin
from .models import Cow, Lactation, LactationData, MultiparousFeatures, Prediction, PrimiparousFeatures

# Register your models here.
admin.site.register(Cow)
admin.site.register(Lactation)
admin.site.register(LactationData)
admin.site.register(MultiparousFeatures)
admin.site.register(PrimiparousFeatures)
admin.site.register(Prediction)
