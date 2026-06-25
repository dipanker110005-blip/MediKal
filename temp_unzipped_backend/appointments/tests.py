from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment

User = get_user_model()

class AppointmentAPITests(APITestCase):
    def setUp(self):
        # Create Patient
        self.patient_user = User.objects.create_user(
            email='patient@medikal.local',
            full_name='John Patient',
            password='Password123',
            role='PATIENT'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            age=25,
            blood_group='O+'
        )

        # Create Doctor
        self.doctor_user = User.objects.create_user(
            email='doctor@medikal.local',
            full_name='Dr. Smith',
            password='Password123',
            role='DOCTOR'
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization='General Physician',
            qualification='MD Medicine',
            experience=8,
            consultation_fee=100.00,
            verification_status='APPROVED'
        )

    def test_create_appointment_success(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-list-create')  # DefaultRouter url name for list/create
        data = {
            'doctor': self.doctor.id,
            'date': timezone.now().date().strftime('%Y-%m-%d'),
            'time': '10:00 AM',
            'consultation_type': 'ONLINE'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.total_fee, Decimal('100.00'))
        self.assertEqual(appointment.status, 'PENDING')

    def test_create_appointment_with_discount(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-list-create')
        data = {
            'doctor': self.doctor.id,
            'date': timezone.now().date().strftime('%Y-%m-%d'),
            'time': '11:00 AM',
            'consultation_type': 'OFFLINE',
            'referral_code': 'MEDIKAL20'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        appointment = Appointment.objects.first()
        # 100.00 - 20% = 80.00
        self.assertEqual(appointment.total_fee, Decimal('80.00'))
        self.assertEqual(appointment.referral_code, 'MEDIKAL20')

    def test_create_appointment_invalid_discount(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-list-create')
        data = {
            'doctor': self.doctor.id,
            'date': timezone.now().date().strftime('%Y-%m-%d'),
            'time': '11:00 AM',
            'consultation_type': 'OFFLINE',
            'referral_code': 'INVALIDCODE'
        }
        response = self.client.post(url, data)
        # Should fail validation due to invalid referral code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('referral_code', response.data)
