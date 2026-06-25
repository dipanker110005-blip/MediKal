import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from emergency.models import EmergencyRequest
from medicines.models import Prescription, MedicineOrder
from notifications.models import Notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with realistic demo data'

    def handle(self, *args, **kwargs):
        # Skip seeding if other users already exist to prevent data loss on restarts
        if User.objects.exclude(email='admin@medikal.local').exists():
            self.stdout.write('Database already contains registered users/patients/doctors. Skipping seed to protect production data.')
            return

        self.stdout.write('Clearing existing data...')
        Notification.objects.all().delete()
        EmergencyRequest.objects.all().delete()
        MedicineOrder.objects.all().delete()
        Prescription.objects.all().delete()
        Appointment.objects.all().delete()
        Patient.objects.all().delete()
        Doctor.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write('Seeding Admin account...')
        admin_user = User.objects.create_user(
            email='admin@medikal.local',
            full_name='System Admin',
            password='Password123',
            role='ADMIN',
            is_staff=True
        )

        self.stdout.write('Seeding Patients...')
        patients_data = [
            {'email': 'patient1@medikal.local', 'full_name': 'John Doe', 'age': 28, 'blood_group': 'O+', 'address': '123 Main St, New York, NY', 'emergency_contact': '+1 (555) 019-2834'},
            {'email': 'patient2@medikal.local', 'full_name': 'Jane Smith', 'age': 45, 'blood_group': 'A-', 'address': '456 Oak Ave, Boston, MA', 'emergency_contact': '+1 (555) 014-9821'},
            {'email': 'patient3@medikal.local', 'full_name': 'Robert Johnson', 'age': 67, 'blood_group': 'B+', 'address': '789 Pine Rd, Chicago, IL', 'emergency_contact': '+1 (555) 012-7489'}
        ]

        patients = []
        for p_info in patients_data:
            user = User.objects.create_user(
                email=p_info['email'],
                full_name=p_info['full_name'],
                password='Password123',
                role='PATIENT'
            )
            patient = Patient.objects.create(
                user=user,
                age=p_info['age'],
                blood_group=p_info['blood_group'],
                address=p_info['address'],
                emergency_contact=p_info['emergency_contact']
            )
            patients.append(patient)

        self.stdout.write('Seeding Doctors...')
        doctors_data = [
            {'email': 'doctor1@medikal.local', 'full_name': 'Sarah Jenkins', 'specialization': 'Cardiologist', 'qualification': 'MD, FACC - Harvard Medical', 'experience': 14, 'fee': 200.00, 'bio': 'Specialist in cardiovascular diseases and preventive care.', 'status': 'APPROVED', 'online': True, 'rating': 4.9},
            {'email': 'doctor2@medikal.local', 'full_name': 'David Chen', 'specialization': 'Dermatologist', 'qualification': 'MD - Stanford Dermatology', 'experience': 8, 'fee': 150.00, 'bio': 'Expert in skin cancer screening, acne treatments, and cosmetic procedures.', 'status': 'APPROVED', 'online': False, 'rating': 4.7},
            {'email': 'doctor3@medikal.local', 'full_name': 'Michael Jordan', 'specialization': 'General Physician', 'qualification': 'MD - Johns Hopkins', 'experience': 20, 'fee': 100.00, 'bio': 'Comprehensive family health care physician with two decades of experience.', 'status': 'APPROVED', 'online': True, 'rating': 4.9},
            {'email': 'doctor4@medikal.local', 'full_name': 'Emily Watson', 'specialization': 'Pediatrician', 'qualification': 'MD - Yale Pediatrics', 'experience': 11, 'fee': 120.00, 'bio': 'Caring pediatrician specializing in developmental care and vaccinations.', 'status': 'APPROVED', 'online': True, 'rating': 4.8},
            {'email': 'doctor5@medikal.local', 'full_name': 'Robert Martinez', 'specialization': 'Orthopedic', 'qualification': 'MD - Columbia Orthopedics', 'experience': 15, 'fee': 180.00, 'bio': 'Specialist in sports injuries, joint replacement, and arthroscopic surgeries.', 'status': 'APPROVED', 'online': False, 'rating': 4.6},
            {'email': 'doctor6@medikal.local', 'full_name': 'Pending Doctor', 'specialization': 'Cardiologist', 'qualification': 'MD - NYU Medicine', 'experience': 5, 'fee': 140.00, 'bio': 'Looking forward to joining the MediKal provider network.', 'status': 'PENDING', 'online': False, 'rating': 5.0}
        ]

        doctors = []
        for d_info in doctors_data:
            user = User.objects.create_user(
                email=d_info['email'],
                full_name=d_info['full_name'],
                password='Password123',
                role='DOCTOR'
            )
            doctor = Doctor.objects.create(
                user=user,
                specialization=d_info['specialization'],
                qualification=d_info['qualification'],
                experience=d_info['experience'],
                consultation_fee=Decimal(d_info['fee']),
                bio=d_info['bio'],
                verification_status=d_info['status'],
                online_status=d_info['online'],
                rating=Decimal(d_info['rating'])
            )
            doctors.append(doctor)

        # Separate approved doctors for appointments
        approved_doctors = [d for d in doctors if d.verification_status == 'APPROVED']

        self.stdout.write('Seeding Appointments...')
        time_slots = ['09:00 AM', '10:00 AM', '11:00 AM', '02:00 PM', '03:00 PM', '04:00 PM']
        types = ['ONLINE', 'OFFLINE']

        today = timezone.now().date()

        # Seed past appointments (last 30 days) to generate revenue history
        for i in range(1, 15):
            patient = random.choice(patients)
            doctor = random.choice(approved_doctors)
            # past date
            date = today - timedelta(days=random.randint(1, 28))
            status_choice = random.choice(['COMPLETED', 'CANCELLED'])
            
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=date,
                time=random.choice(time_slots),
                consultation_type=random.choice(types),
                status=status_choice,
                total_fee=doctor.consultation_fee
            )

        # Seed today's appointments
        for patient in patients:
            doctor = random.choice(approved_doctors)
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=today,
                time=random.choice(time_slots),
                consultation_type=random.choice(types),
                status='CONFIRMED',
                total_fee=doctor.consultation_fee
            )

        # Seed future appointments (next week)
        for i in range(1, 6):
            patient = random.choice(patients)
            doctor = random.choice(approved_doctors)
            date = today + timedelta(days=random.randint(1, 7))
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=date,
                time=random.choice(time_slots),
                consultation_type=random.choice(types),
                status='PENDING',
                total_fee=doctor.consultation_fee
            )

        self.stdout.write('Seeding Prescriptions & Medicine Orders...')
        for idx, patient in enumerate(patients):
            doctor = random.choice(approved_doctors)
            # Seed Prescription
            prescription = Prescription.objects.create(
                patient=patient,
                doctor=doctor,
                image='prescriptions/demo_prescription.jpg',
                notes=f'Take one pill daily after dinner. Keep hydrated.'
            )
            # Seed corresponding order
            order_status = random.choice(['RECEIVED', 'VERIFIED', 'PACKED', 'OUT_FOR_DELIVERY', 'DELIVERED'])
            MedicineOrder.objects.create(
                patient=patient,
                prescription=prescription,
                delivery_address=patient.address,
                contact_number='+1 (555) 012-3456',
                status=order_status,
                total_price=Decimal(random.randint(25, 120))
            )

        self.stdout.write('Seeding GPS Emergency Requests...')
        # Ny coordinate offset mock
        emergency_locs = [
            (40.7128, -74.0060),  # NYC
            (42.3601, -71.0589),  # Boston
            (41.8781, -87.6298),  # Chicago
        ]
        for idx, patient in enumerate(patients):
            lat, lng = emergency_locs[idx % len(emergency_locs)]
            EmergencyRequest.objects.create(
                patient=patient,
                latitude=Decimal(lat),
                longitude=Decimal(lng),
                status=random.choice(['PENDING', 'DISPATCHED', 'RESOLVED'])
            )

        self.stdout.write('Seeding Notifications...')
        # Seed notifications for patients & doctors
        for p in patients:
            Notification.objects.create(
                user=p.user,
                title='Welcome to MediKal!',
                body='Thank you for setting up your profile. Explore consultations and prescription delivery!',
                is_read=False
            )
            Notification.objects.create(
                user=p.user,
                title='Appointment Booked',
                body='Your upcoming appointment is confirmed for this week.',
                is_read=True
            )

        for d in approved_doctors:
            Notification.objects.create(
                user=d.user,
                title='New Schedule Alert',
                body='A new patient has scheduled an appointment on your dashboard calendar.',
                is_read=False
            )

        self.stdout.write(self.style.SUCCESS('Database successfully seeded with realistic dummy data!'))
