from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from .models import Doctor
from .serializers import DoctorSerializer, DoctorVerificationSerializer

from accounts.permissions import IsAdmin

class DoctorListView(generics.ListAPIView):
    """
    API view to list approved doctors.
    Supports filtering by 'specialization' query parameter.
    """
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Only show approved doctors
        queryset = Doctor.objects.filter(verification_status='APPROVED')
        
        # Filter by specialization if query param is provided
        specialization = self.request.query_params.get('specialization', None)
        if specialization and specialization != 'All':
            queryset = queryset.filter(specialization=specialization)
            
        return queryset

class DoctorDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve details of a specific doctor.
    """
    queryset = Doctor.objects.filter(verification_status='APPROVED')
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]

class DoctorVerificationListView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        status_param = self.request.query_params.get('status', 'PENDING')
        # We can verify PENDING, APPROVED, or REJECTED doctors
        return Doctor.objects.filter(verification_status=status_param).order_by('-created_at')

class DoctorVerificationUpdateView(generics.UpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorVerificationSerializer
    permission_classes = [IsAdmin]


from django.db import transaction
from .serializers import DoctorCreateSerializer, DoctorAdminUpdateSerializer

class DoctorAdminListCreateView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all().order_by('-created_at')
    permission_classes = [IsAdmin]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DoctorCreateSerializer
        return DoctorAdminUpdateSerializer

class DoctorAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorAdminUpdateSerializer
    permission_classes = [IsAdmin]

    @transaction.atomic
    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()

