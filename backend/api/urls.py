from django.urls import path
from . import views

urlpatterns = [
    path("data/upload/", views.DataUploadView.as_view(), name="data-upload"),
]
