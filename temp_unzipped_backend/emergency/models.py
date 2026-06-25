from django.db import models
from django.conf import settings
from patients.models import Patient

class EmergencyRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Dispatch'),
        ('DISPATCHED', 'Ambulance Dispatched'),
        ('RESOLVED', 'Resolved'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_requests')
    latitude = models.DecimalField(max_digits=12, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Emergency Alert #{self.id} for {self.patient.user.full_name} ({self.status})"
