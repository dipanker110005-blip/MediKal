from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Prescription, MedicineOrder
from .serializers import PrescriptionSerializer, MedicineOrderSerializer

class PrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return Prescription.objects.filter(patient=user.patient_profile).order_by('-created_at')
        elif hasattr(user, 'doctor_profile'):
            return Prescription.objects.filter(doctor=user.doctor_profile).order_by('-created_at')
        elif user.is_staff or user.role == 'ADMIN':
            return Prescription.objects.all().order_by('-created_at')
        return Prescription.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            serializer.save(patient=user.patient_profile)
        else:
            serializer.save()

class MedicineOrderViewSet(viewsets.ModelViewSet):
    serializer_class = MedicineOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return MedicineOrder.objects.filter(patient=user.patient_profile).order_by('-created_at')
        elif user.is_staff or user.role == 'ADMIN':
            return MedicineOrder.objects.all().order_by('-created_at')
        return MedicineOrder.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            serializer.save(patient=user.patient_profile)
        else:
            serializer.save()

    def perform_update(self, serializer):
        order = serializer.save()
        try:
            from notifications.utils import send_notification
            status = order.status
            status_titles = {
                'VERIFIED': 'Order Verified',
                'PACKED': 'Order Packed',
                'OUT_FOR_DELIVERY': 'Out for Delivery!',
                'DELIVERED': 'Order Delivered 🎉',
            }
            title = status_titles.get(status, f"Order Update: {status}")
            body = f"Your medicine order #{order.id} status is now: {status.replace('_', ' ').title()}."
            
            if status == 'VERIFIED' and order.total_price > 0:
                body += f" Total price is verified at ${order.total_price}."
            
            send_notification(
                user=order.patient.user,
                title=title,
                body=body
            )
        except Exception as e:
            print(f"Failed to trigger order update notification: {e}")
