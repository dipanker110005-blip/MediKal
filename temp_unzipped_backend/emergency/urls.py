from django.urls import path
from .views import EmergencyRequestListCreateView, NearbyFacilitiesView

urlpatterns = [
    path('', EmergencyRequestListCreateView.as_view(), name='emergency-request-list-create'),
    path('nearby/', NearbyFacilitiesView.as_view(), name='nearby-facilities'),
]
