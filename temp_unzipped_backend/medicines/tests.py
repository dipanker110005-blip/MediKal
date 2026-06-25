from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal

from patients.models import Patient
from doctors.models import Doctor
from medicines.models import Prescription, MedicineOrder

User = get_user_model()

class MedicinesAPITests(APITestCase):
    def setUp(self):
        # Create Patient A
        self.patient_user_a = User.objects.create_user(
            email='patienta@medikal.local',
            full_name='Patient A',
            password='Password123',
            role='PATIENT'
        )
        self.patient_a = Patient.objects.create(
            user=self.patient_user_a,
            age=25,
            blood_group='O+'
        )

        # Create Patient B
        self.patient_user_b = User.objects.create_user(
            email='patientb@medikal.local',
            full_name='Patient B',
            password='Password123',
            role='PATIENT'
        )
        self.patient_b = Patient.objects.create(
            user=self.patient_user_b,
            age=35,
            blood_group='AB-'
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
            specialization='Dermatologist',
            qualification='MD Dermatology',
            experience=5,
            consultation_fee=120.00,
            verification_status='APPROVED'
        )

        # Create Prescription and Order for Patient A
        # Create a mock image file
        self.mock_image = SimpleUploadedFile(
            name='prescription.jpg',
            content=b'mock_image_data',
            content_type='image/jpeg'
        )
        self.prescription_a = Prescription.objects.create(
            patient=self.patient_a,
            doctor=self.doctor,
            image=self.mock_image,
            notes='Acne cream twice daily.'
        )
        self.order_a = MedicineOrder.objects.create(
            patient=self.patient_a,
            prescription=self.prescription_a,
            delivery_address='123 Main St',
            contact_number='1234567890',
            status='RECEIVED',
            total_price=Decimal('45.00')
        )

    def test_upload_prescription_success(self):
        self.client.force_authenticate(user=self.patient_user_a)
        url = reverse('prescription-list')
        
        # Test file upload
        test_file = SimpleUploadedFile(
            name='new_prescription.jpg',
            content=b'new_image_data',
            content_type='image/jpeg'
        )
        
        data = {
            'patient': self.patient_a.id,
            'doctor': self.doctor.id,
            'notes': 'Flu medicine.',
            'image': test_file
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Prescription.objects.count(), 2)

    def test_create_medicine_order_success(self):
        self.client.force_authenticate(user=self.patient_user_a)
        url = reverse('medicineorder-list')
        data = {
            'patient': self.patient_a.id,
            'prescription': self.prescription_a.id,
            'delivery_address': '456 Oak Rd',
            'contact_number': '0987654321'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicineOrder.objects.count(), 2)

    def test_patient_queryset_restriction(self):
        # Authenticate Patient B
        self.client.force_authenticate(user=self.patient_user_b)
        
        # Patient B tries to get orders list
        url = reverse('medicineorder-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return 0 orders because Patient B has no orders, and cannot view Patient A's orders!
        self.assertEqual(len(response.data), 0)
        
        # Patient B tries to retrieve Patient A's order details directly
        detail_url = reverse('medicineorder-detail', kwargs={'pk': self.order_a.id})
        response = self.client.get(detail_url)
        # Should return 404 Not Found since it is excluded from Patient B's queryset
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
