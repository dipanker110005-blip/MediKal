from django.db import models
from django.conf import settings

class Doctor(models.Model):
    VERIFICATION_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    SPECIALIZATION_CHOICES = (
        ('Cardiologist', 'Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('General Physician', 'General Physician'),
        ('Pediatrician', 'Pediatrician'),
        ('Orthopedic', 'Orthopedic'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    qualification = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_CHOICES, default='PENDING')
    online_status = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.full_name} ({self.specialization})"
