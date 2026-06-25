from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIRequestFactory

from accounts.permissions import IsPatient, IsDoctor, IsAdmin

User = get_user_model()
from accounts.models import RegistrationOTP

class AccountsSecurityTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            email='testuser@medikal.local',
            full_name='Test User',
            password='Password123!',
            role='PATIENT'
        )
        self.doctor_user = User.objects.create_user(
            email='testdoc@medikal.local',
            full_name='Test Doc',
            password='Password123!',
            role='DOCTOR'
        )
        self.admin_user = User.objects.create_user(
            email='testadmin@medikal.local',
            full_name='Test Admin',
            password='Password123!',
            role='ADMIN',
            is_staff=True
        )

    def tearDown(self):
        cache.clear()

    def test_login_rate_limiting(self):
        url = reverse('login')
        
        # Send 10 requests (all should return 401 Unauthorized due to wrong password)
        for i in range(10):
            response = self.client.post(url, {
                'email': 'testuser@medikal.local',
                'password': 'WrongPassword123'
            })
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            
        # The 11th request within the same minute should be throttled (429 Too Many Requests)
        response = self.client.post(url, {
            'email': 'testuser@medikal.local',
            'password': 'WrongPassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_login_succeeds_directly(self):
        url = reverse('login')
        response = self.client.post(url, {
            'email': 'testuser@medikal.local',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data.get('email'), 'testuser@medikal.local')

    def test_send_otp_success(self):
        url = reverse('register-send-otp')
        response = self.client.post(url, {
            'type': 'email',
            'value': 'newuser@medikal.local'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sent to your email', response.data.get('detail'))
        
        # Check record created in database
        otp_record = RegistrationOTP.objects.get(type='email', value='newuser@medikal.local')
        self.assertEqual(len(otp_record.otp_code), 6)
        self.assertFalse(otp_record.verified)

    def test_send_otp_existing_email(self):
        url = reverse('register-send-otp')
        response = self.client.post(url, {
            'type': 'email',
            'value': 'testuser@medikal.local' # already exists
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already exists', response.data.get('detail'))

    def test_verify_otp_success(self):
        # Send OTP first
        self.client.post(reverse('register-send-otp'), {
            'type': 'email',
            'value': 'newuser@medikal.local'
        })
        otp_record = RegistrationOTP.objects.get(type='email', value='newuser@medikal.local')
        
        # Verify
        url = reverse('register-verify-otp')
        response = self.client.post(url, {
            'type': 'email',
            'value': 'newuser@medikal.local',
            'otp': otp_record.otp_code
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('verified'))
        
        otp_record.refresh_from_db()
        self.assertTrue(otp_record.verified)

    def test_verify_otp_incorrect(self):
        self.client.post(reverse('register-send-otp'), {
            'type': 'email',
            'value': 'newuser@medikal.local'
        })
        
        url = reverse('register-verify-otp')
        response = self.client.post(url, {
            'type': 'email',
            'value': 'newuser@medikal.local',
            'otp': '000000' # wrong code
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Incorrect OTP', response.data.get('detail'))

    def test_register_without_otp_fails(self):
        url = reverse('patient-register')
        response = self.client.post(url, {
            'full_name': 'New Patient',
            'email': 'newpatient@medikal.local',
            'phone': '1234567890',
            'password': 'Password123!',
            'age': 25,
            'blood_group': 'O+'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('must be verified via OTP first', response.data.get('detail'))

    def test_register_success(self):
        # 1. Send & verify Email OTP
        self.client.post(reverse('register-send-otp'), {'type': 'email', 'value': 'newpatient@medikal.local'})
        email_record = RegistrationOTP.objects.get(type='email', value='newpatient@medikal.local')
        self.client.post(reverse('register-verify-otp'), {'type': 'email', 'value': 'newpatient@medikal.local', 'otp': email_record.otp_code})
        
        # 2. Send & verify Phone OTP
        self.client.post(reverse('register-send-otp'), {'type': 'phone', 'value': '1234567890'})
        phone_record = RegistrationOTP.objects.get(type='phone', value='1234567890')
        self.client.post(reverse('register-verify-otp'), {'type': 'phone', 'value': '1234567890', 'otp': phone_record.otp_code})
        
        # 3. Register
        url = reverse('patient-register')
        response = self.client.post(url, {
            'full_name': 'New Patient',
            'email': 'newpatient@medikal.local',
            'phone': '1234567890',
            'password': 'Password123!',
            'age': 25,
            'blood_group': 'O+'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data.get('email'), 'newpatient@medikal.local')
        
        # Verify user is created active
        user = User.objects.get(email='newpatient@medikal.local')
        self.assertTrue(user.is_active)
        
        # Verify RegistrationOTP records cleaned up
        self.assertFalse(RegistrationOTP.objects.filter(value='newpatient@medikal.local').exists())
        self.assertFalse(RegistrationOTP.objects.filter(value='1234567890').exists())

    def test_permission_classes_logical_checks(self):
        factory = APIRequestFactory()
        request = factory.get('/')
        
        is_patient_perm = IsPatient()
        is_doctor_perm = IsDoctor()
        is_admin_perm = IsAdmin()

        # Check Patient permissions
        request.user = self.user
        self.assertTrue(is_patient_perm.has_permission(request, None))
        self.assertFalse(is_doctor_perm.has_permission(request, None))
        self.assertFalse(is_admin_perm.has_permission(request, None))

        # Check Doctor permissions
        request.user = self.doctor_user
        self.assertFalse(is_patient_perm.has_permission(request, None))
        self.assertTrue(is_doctor_perm.has_permission(request, None))
        self.assertFalse(is_admin_perm.has_permission(request, None))

        # Check Admin permissions
        request.user = self.admin_user
        self.assertFalse(is_patient_perm.has_permission(request, None))
        self.assertFalse(is_doctor_perm.has_permission(request, None))
        self.assertTrue(is_admin_perm.has_permission(request, None))
