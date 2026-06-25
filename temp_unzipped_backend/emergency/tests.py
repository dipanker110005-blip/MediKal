from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from patients.models import Patient
from emergency.models import EmergencyRequest

User = get_user_model()

class EmergencyAPITests(APITestCase):
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

    def test_create_emergency_request_success(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('emergency-request-list-create')
        data = {
            'patient': self.patient.id,
            'latitude': 40.712800000,
            'longitude': -74.006000000
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EmergencyRequest.objects.count(), 1)
        
        request = EmergencyRequest.objects.first()
        self.assertEqual(request.status, 'PENDING')
        self.assertEqual(request.latitude, Decimal('40.712800000'))

    def test_get_emergency_requests(self):
        self.client.force_authenticate(user=self.patient_user)
        # Seed an emergency request
        EmergencyRequest.objects.create(
            patient=self.patient,
            latitude=Decimal('40.712800000'),
            longitude=Decimal('-74.006000000'),
            status='PENDING'
        )
        
        url = reverse('emergency-request-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_nearby_facilities_success(self):
        url = reverse('nearby-facilities')
        response = self.client.get(url, {'latitude': 40.7128, 'longitude': -74.0060})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIn('hospitals', response.data)
        self.assertIn('clinics', response.data)
        self.assertIn('doctors', response.data)
        self.assertEqual(len(response.data['hospitals']), 3)
        self.assertEqual(len(response.data['clinics']), 2)

    def test_nearby_facilities_missing_params(self):
        url = reverse('nearby-facilities')
        response = self.client.get(url)
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
