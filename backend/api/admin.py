from django.contrib import admin
from .models import Cow, Lactation, LactationData

# Register your models here.
admin.site.register(Cow)
admin.site.register(Lactation)
admin.site.register(LactationData)
