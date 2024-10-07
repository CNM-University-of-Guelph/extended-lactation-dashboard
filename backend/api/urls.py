from django.urls import path
from . import views

urlpatterns = [
    path("data/upload/", views.DataUploadView.as_view(), name="data-upload"),
    path("data/files/", views.ListUserFilesView.as_view(), name="list-user-files"),
    path("data/file/<str:filename>/", views.GetUserFileView.as_view(), name="get-user-file"),
    path('predictions/', views.PredictionsListView.as_view(), name='predictions-list'),
    path('treatments/', views.TreatmentListView.as_view(), name='treatments-list'),
    path('update-treatment-group/<int:lactation_id>/', views.UpdateTreatmentGroupView.as_view(), name='update_treatment_group'),
]
