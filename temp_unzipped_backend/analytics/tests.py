from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment

User = get_user_model()

class AnalyticsAPITests(APITestCase):
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
            age=30,
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
            specialization='Cardiologist',
            qualification='MD Cardiology',
            experience=10,
            consultation_fee=150.00,
            verification_status='APPROVED'
        )

        # Create Admin
        self.admin_user = User.objects.create_user(
            email='admin@medikal.local',
            full_name='Admin User',
            password='Password123',
            role='ADMIN',
            is_staff=True
        )

        # Create Appointments
        self.appointment1 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.now().date(),
            time='10:00 AM',
            consultation_type='ONLINE',
            status='COMPLETED',
            total_fee=150.00
        )
        self.appointment2 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.now().date() - timedelta(days=1),
            time='11:00 AM',
            consultation_type='OFFLINE',
            status='PENDING',
            total_fee=150.00
        )

    def test_admin_analytics_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-analytics-dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['total_revenue'], 150.00)
        self.assertEqual(data['patient_count'], 1)
        self.assertEqual(data['doctor_count'], 1)
        self.assertEqual(data['appointment_count'], 2)
        
        # Breakdown checks
        self.assertEqual(data['status_breakdown']['COMPLETED'], 1)
        self.assertEqual(data['status_breakdown']['PENDING'], 1)
        self.assertEqual(data['specialty_breakdown']['Cardiologist'], 2)
        self.assertEqual(data['type_breakdown']['ONLINE'], 1)
        self.assertEqual(data['type_breakdown']['OFFLINE'], 1)
        
        # Demographics checks
        self.assertEqual(data['age_demographics']['18-35'], 1)
        self.assertEqual(data['blood_group_breakdown']['O+'], 1)
        
        # Timeline checks
        self.assertEqual(len(data['revenue_timeline']), 30)
        self.assertEqual(data['revenue_timeline'][-1]['revenue'], 150.00)

    def test_admin_analytics_forbidden_for_patient(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('admin-analytics-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_doctor_analytics_success(self):
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctor-analytics')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['total_consultations'], 1)
        self.assertEqual(data['total_earnings'], 150.00)
        self.assertEqual(data['patient_count'], 1)
        self.assertEqual(data['rating'], 5.0)
        self.assertEqual(data['status_breakdown']['COMPLETED'], 1)
        self.assertEqual(data['status_breakdown']['PENDING'], 1)
        self.assertEqual(data['type_breakdown']['ONLINE'], 1)
        self.assertEqual(data['type_breakdown']['OFFLINE'], 1)
        self.assertEqual(len(data['earnings_timeline']), 30)
        self.assertEqual(data['earnings_timeline'][-1]['earnings'], 150.00)

    def test_doctor_analytics_forbidden_for_patient(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctor-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
