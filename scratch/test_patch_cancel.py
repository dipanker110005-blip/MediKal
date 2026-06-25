import os
import django
import sys

sys.path.append('C:/Users/OM/OneDrive/Desktop/MediKal/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medikal_backend.settings')
django.setup()

from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer
from django.contrib.auth import get_user_model

# Get any confirmed or pending appointment
appointment = Appointment.objects.filter(status__in=['CONFIRMED', 'PENDING']).first()

if not appointment:
    # Create one to test
    print("No active appointment found, creating a test one...")
    from patients.models import Patient
    from doctors.models import Doctor
    patient = Patient.objects.first()
    doctor = Doctor.objects.first()
    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        date="2026-06-12",
        time="10:00 AM",
        consultation_type="ONLINE",
        total_fee=150.00,
        status="PENDING"
    )

print(f"Before update: ID={appointment.id}, Status={appointment.status}")

# Simulate PATCH request data
data = {'status': 'CANCELLED'}
serializer = AppointmentSerializer(appointment, data=data, partial=True)
print("Is valid?", serializer.is_valid())
if not serializer.is_valid():
    print("Errors:", serializer.errors)
else:
    updated_instance = serializer.save()
    print(f"After update inside code: ID={updated_instance.id}, Status={updated_instance.status}")
    
    # Reload from DB
    reloaded = Appointment.objects.get(id=appointment.id)
    print(f"After update reloaded from DB: ID={reloaded.id}, Status={reloaded.status}")
