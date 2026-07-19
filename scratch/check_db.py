import os
import django
import sys

# Set up django environment
sys.path.append('C:/Users/OM/OneDrive/Desktop/MediKal/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medikal_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from appointments.models import Appointment
from notifications.models import Notification

User = get_user_model()

print("=== Users ===")
for u in User.objects.all():
    print(f"ID: {u.id}, Email: {u.email}, Name: {u.full_name}, Role: {u.role}")

print("\n=== Appointments ===")
for a in Appointment.objects.all():
    print(f"ID: {a.id}, Patient: {a.patient.user.email}, Doctor: {a.doctor.user.full_name}, Status: {a.status}, Date: {a.date}")

print("\n=== Notifications ===")
for n in Notification.objects.all():
    print(f"ID: {n.id}, User: {n.user.email}, Title: {n.title}, Read: {n.is_read}, Created: {n.created_at}")
