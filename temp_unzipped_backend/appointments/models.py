from django.db import models
from django.conf import settings
from patients.models import Patient
from doctors.models import Doctor

class Appointment(models.Model):
    CONSULTATION_CHOICES = (
        ('ONLINE', 'Online Video Consultation'),
        ('OFFLINE', 'In-Person Visit'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.CharField(max_length=20)  # Time slot text, e.g., '10:30 AM'
    consultation_type = models.CharField(max_length=10, choices=CONSULTATION_CHOICES, default='ONLINE')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    referral_code = models.CharField(max_length=50, blank=True, null=True)
    total_fee = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Razorpay payment tracking fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __print__(self):
        return f"Appointment: {self.patient.user.full_name} with Dr. {self.doctor.user.full_name} on {self.date}"
