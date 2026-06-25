from rest_framework import generics
from django.db import transaction
from accounts.permissions import IsAdmin
from .models import Patient
from .serializers import PatientSerializer

class PatientAdminListView(generics.ListAPIView):
    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientSerializer
    permission_classes = [IsAdmin]

class PatientAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAdmin]

    @transaction.atomic
    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()
