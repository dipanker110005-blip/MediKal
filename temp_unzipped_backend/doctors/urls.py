from django.urls import path
from .views import (
    DoctorListView, 
    DoctorDetailView, 
    DoctorVerificationListView, 
    DoctorVerificationUpdateView,
    DoctorAdminListCreateView,
    DoctorAdminDetailView
)

urlpatterns = [
    path('', DoctorListView.as_view(), name='doctor-list'),
    path('<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('verification/', DoctorVerificationListView.as_view(), name='doctor-verification-list'),
    path('<int:pk>/verify/', DoctorVerificationUpdateView.as_view(), name='doctor-verification-update'),
    path('admin/', DoctorAdminListCreateView.as_view(), name='doctor-admin-list'),
    path('admin/<int:pk>/', DoctorAdminDetailView.as_view(), name='doctor-admin-detail'),
]
