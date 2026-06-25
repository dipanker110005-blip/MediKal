from django.db import models
from django.conf import settings
from patients.models import Patient
from doctors.models import Doctor

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescribed_prescriptions')
    image = models.FileField(upload_to='prescriptions/')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        doctor_name = f"Dr. {self.doctor.user.full_name}" if self.doctor else "Self Upload"
        return f"Prescription #{self.id} - {self.patient.user.full_name} ({doctor_name})"

class MedicineOrder(models.Model):
    STATUS_CHOICES = (
        ('RECEIVED', 'Received'),
        ('VERIFIED', 'Verified'),
        ('PACKED', 'Packed'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medicine_orders')
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    delivery_address = models.TextField()
    contact_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RECEIVED')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.patient.user.full_name} ({self.status})"
