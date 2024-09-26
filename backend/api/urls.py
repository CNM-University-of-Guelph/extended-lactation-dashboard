from django.urls import path
from . import views

urlpatterns = [
    path("data/upload/", views.DataUploadView.as_view(), name="data-upload"),
    path("data/files/", views.ListUserFilesView.as_view(), name="list-user-files"),
    path("data/file/<str:filename>/", views.GetUserFileView.as_view(), name="get-user-file"),
]
