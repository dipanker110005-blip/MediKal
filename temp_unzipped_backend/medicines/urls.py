from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet, MedicineOrderViewSet

router = DefaultRouter()
router.register('prescriptions', PrescriptionViewSet, basename='prescription')
router.register('orders', MedicineOrderViewSet, basename='medicineorder')

urlpatterns = [
    path('', include(router.urls)),
]

