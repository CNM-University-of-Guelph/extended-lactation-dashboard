from django.urls import path
from . import views

urlpatterns = [
    path("data/upload/", views.DataUploadView.as_view(), name="data-upload"),
    path("data/files/", views.ListUserFilesView.as_view(), name="list-user-files"),
    path("data/file/<str:filename>/", views.GetUserFileView.as_view(), name="get-user-file"),
    path('predictions/', views.PredictionsListView.as_view(), name='predictions-list'),
    path('treatments/', views.TreatmentListView.as_view(), name='treatments-list'),
    path('update-treatment-group/<int:lactation_id>/', views.UpdateTreatmentGroupView.as_view(), name='update_treatment_group'),
    path('lactation-data/', views.LactationDataListView.as_view(), name="lactation-data"),
    path('multiparous-features/', views.MultiparousFeaturesListView.as_view(), name="multiparous-features"),
    path('primiparous-features/', views.PrimiparousFeaturesListView.as_view(), name="primiparous-features"),
    path('profile/info/', views.CurrentUserView.as_view(), name='user-info'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('profile/change-email/', views.ChangeEmailView.as_view(), name='change-email'),
    path('profile/delete/', views.DeleteUserView.as_view(), name='delete-account'),
]
