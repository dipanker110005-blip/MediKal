from django.urls import path
from .views import PatientAdminListView, PatientAdminDetailView

urlpatterns = [
    path('admin/', PatientAdminListView.as_view(), name='patient-admin-list'),
    path('admin/<int:pk>/', PatientAdminDetailView.as_view(), name='patient-admin-detail'),
]
