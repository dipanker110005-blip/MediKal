import os
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import random
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import PatientRegisterSerializer, UserSerializer, PatientProfileSerializer
from patients.models import Patient
from doctors.models import Doctor
from doctors.serializers import DoctorProfileUpdateSerializer

User = get_user_model()
from .models import RegistrationOTP

from rest_framework.throttling import ScopedRateThrottle
from django.core.mail import send_mail
from django.conf import settings
import urllib.request
import urllib.parse
import urllib.error
import base64

def send_twilio_sms(to_number, body):
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
    
    if not account_sid or not auth_token or not from_number:
        return False, "Twilio environment credentials missing."

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    formatted_to = to_number.strip()
    if not formatted_to.startswith('+'):
        if len(formatted_to) == 10:
            formatted_to = f"+91{formatted_to}"
        else:
            formatted_to = f"+{formatted_to}"

    data = urllib.parse.urlencode({
        'From': from_number,
        'To': formatted_to,
        'Body': body
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    auth_str = f"{account_sid}:{auth_token}"
    auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    req.add_header('Authorization', f'Basic {auth_b64}')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            print(f"SMS successfully sent to {formatted_to}. Twilio response: {res_body}")
            return True, None
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
            import json
            err_data = json.loads(err_body)
            err_msg = err_data.get('message', err_body)
        except Exception:
            err_msg = e.reason
        msg = f"Twilio API error {e.code}: {err_msg}"
        print(msg)
        return False, msg
    except Exception as e:
        msg = f"Twilio connection error: {str(e)}"
        print(msg)
        return False, msg


def send_fast2sms_otp(to_number, otp_code):
    api_key = getattr(settings, 'FAST2SMS_API_KEY', '')
    if not api_key:
        return False, "Fast2SMS API key is missing."
        
    url = "https://www.fast2sms.com/dev/bulkV2"
    
    phone_clean = ''.join(filter(str.isdigit, to_number))
    if len(phone_clean) >= 10:
        phone_clean = phone_clean[-10:]
    else:
        return False, f"Invalid phone number length for Fast2SMS: {to_number}"

    data = {
        'route': 'otp',
        'variables_values': otp_code,
        'numbers': phone_clean
    }
    
    headers = {
        'authorization': api_key,
        'Content-Type': 'application/json'
    }
    
    import json
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            res_data = json.loads(res_body)
            if res_data.get('return') is True:
                print(f"Fast2SMS OTP sent successfully to {phone_clean}.")
                return True, None
            else:
                msg = f"Fast2SMS API returned failure: {res_data.get('message', res_body)}"
                print(msg)
                return False, msg
    except urllib.error.HTTPError as e:
        msg = f"Fast2SMS HTTP error: {e.code} - {e.reason}"
        print(msg)
        return False, msg
    except Exception as e:
        msg = f"Fast2SMS connection error: {str(e)}"
        print(msg)
        return False, msg


def send_resend_email(to_email, subject, html_content):
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if not api_key:
        return False, "Resend API Key is missing."
        
    url = "https://api.resend.com/emails"
    data = {
        "from": "MediKal <onboarding@resend.dev>",
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    import json
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            print(f"Resend email sent successfully. Response: {res_body}")
            return True, None
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
            err_data = json.loads(err_body)
            err_msg = err_data.get('message', err_body)
        except Exception:
            err_msg = e.reason
        msg = f"Resend API error {e.code}: {err_msg}"
        print(msg)
        return False, msg
    except Exception as e:
        msg = f"Resend connection error: {str(e)}"
        print(msg)
        return False, msg


def send_brevo_email(to_email, subject, html_content):
    api_key = getattr(settings, 'BREVO_API_KEY', '')
    if not api_key:
        return False, "Brevo API Key is missing."
        
    sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '') or 'onboarding@brevo.dev'
    
    url = "https://api.brevo.com/v3/smtp/email"
    data = {
        "sender": {"name": "MediKal", "email": sender_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content
    }
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    import json
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            res_data = json.loads(res_body)
            if res_data.get('return') is True or 'messageId' in res_data:
                print(f"Brevo email sent successfully. Response: {res_body}")
                return True, None
            else:
                msg = f"Brevo API returned failure: {res_body}"
                print(msg)
                return False, msg
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
            err_data = json.loads(err_body)
            err_msg = err_data.get('message', err_body)
        except Exception:
            err_msg = e.reason
        msg = f"Brevo API error {e.code}: {err_msg}"
        print(msg)
        return False, msg
    except Exception as e:
        msg = f"Brevo connection error: {str(e)}"
        print(msg)
        return False, msg


def send_email_helper(to_email, subject, text_message, html_message):
    if getattr(settings, 'RESEND_API_KEY', ''):
        success, err = send_resend_email(to_email, subject, html_message)
        return success, err, "Resend"
    elif getattr(settings, 'BREVO_API_KEY', ''):
        success, err = send_brevo_email(to_email, subject, html_message)
        return success, err, "Brevo"
    elif settings.EMAIL_HOST_USER:
        try:
            send_mail(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                fail_silently=False
            )
            print(f"Real verification email sent via SMTP to {to_email}")
            return True, None, "SMTP"
        except Exception as e:
            msg = f"SMTP error: {str(e)}"
            print(msg)
            return False, msg, "SMTP"
    else:
        # Console email fallback
        try:
            send_mail(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                fail_silently=False
            )
            print(f"Verification email printed to console/logs for {to_email}")
            return True, None, "Console"
        except Exception as e:
            msg = f"Console printer error: {str(e)}"
            print(msg)
            return False, msg, "Console"


class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_attempt'

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)
        if user is not None:
            if not user.is_active:
                return Response({"detail": "User account is disabled or unverified."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate JWT tokens directly
            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }, status=status.HTTP_200_OK)

        return Response({"detail": "No active account found with the given credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class SendRegistrationOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_attempt'

    def post(self, request):
        otp_type = request.data.get('type')  # 'email' or 'phone'
        value = request.data.get('value')
        email = request.data.get('email')  # Optional email for phone verification fallback

        if not otp_type or not value:
            return Response({"detail": "Type and value are required."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_type not in ['email', 'phone']:
            return Response({"detail": "Invalid type. Must be 'email' or 'phone'."}, status=status.HTTP_400_BAD_REQUEST)

        # Uniqueness check against active users
        if otp_type == 'email':
            value = value.strip().lower()
            if User.objects.filter(email=value, is_active=True).exists():
                return Response({"detail": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            value = value.strip()
            if User.objects.filter(phone=value, is_active=True).exists():
                return Response({"detail": "A user with this phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp = f"{random.randint(100000, 999999)}"
        
        # Create or update RegistrationOTP record
        RegistrationOTP.objects.update_or_create(
            type=otp_type,
            value=value,
            defaults={
                'otp_code': otp,
                'expires_at': timezone.now() + timedelta(minutes=5),
                'verified': False
            }
        )

        has_email_provider = bool(
            getattr(settings, 'RESEND_API_KEY', '') or 
            getattr(settings, 'BREVO_API_KEY', '') or 
            getattr(settings, 'EMAIL_HOST_USER', '')
        )
        
        has_sms_provider = bool(
            (getattr(settings, 'TWILIO_ACCOUNT_SID', '') and getattr(settings, 'TWILIO_AUTH_TOKEN', '') and getattr(settings, 'TWILIO_PHONE_NUMBER', '')) or
            getattr(settings, 'FAST2SMS_API_KEY', '')
        )

        real_sent = False
        error_detail = None

        if otp_type == 'email':
            subject = "MediKal Email Verification Code"
            message = f"Your MediKal verification code is: {otp}\n\nThis code is valid for 5 minutes."
            html_message = f"<p>Your MediKal verification code is: <strong>{otp}</strong></p><p>This code is valid for 5 minutes.</p>"
            success, err, provider = send_email_helper(value, subject, message, html_message)
            if success:
                if provider != "Console":
                    real_sent = True
            else:
                error_detail = err
        else:
            if getattr(settings, 'TWILIO_ACCOUNT_SID', '') and getattr(settings, 'TWILIO_AUTH_TOKEN', '') and getattr(settings, 'TWILIO_PHONE_NUMBER', ''):
                message_body = f"Your MediKal verification code is: {otp}. Valid for 5 minutes."
                success, err = send_twilio_sms(value, message_body)
                if success:
                    real_sent = True
                else:
                    error_detail = err
            elif getattr(settings, 'FAST2SMS_API_KEY', ''):
                success, err = send_fast2sms_otp(value, otp)
                if success:
                    real_sent = True
                else:
                    error_detail = err
            elif email and has_email_provider:
                # Fallback: Send Phone OTP to Email!
                subject = "MediKal Phone Verification Code"
                message = f"Your MediKal phone verification code for {value} is: {otp}\n\nThis code is valid for 5 minutes."
                html_message = f"<p>Your MediKal phone verification code for {value} is: <strong>{otp}</strong></p><p>This code is valid for 5 minutes.</p>"
                success, err, provider = send_email_helper(email, subject, message, html_message)
                if success:
                    if provider != "Console":
                        real_sent = True
                    print(f"Phone verification email sent to {email} as SMS fallback")
                else:
                    error_detail = f"Could not send email fallback: {err}"
            else:
                print("========================================")
                print(f"Registration Phone OTP generated for {value}: {otp} (Twilio/Fast2SMS/Email fallback not configured)")
                print("========================================")

        # Handle failure when a provider was intended but failed
        if otp_type == 'email' and has_email_provider and not real_sent:
            return Response({
                "detail": f"Failed to send email verification: {error_detail or 'Unknown error'}"
            }, status=status.HTTP_400_BAD_REQUEST)

        if otp_type == 'phone' and (has_sms_provider or (email and has_email_provider)) and not real_sent:
            return Response({
                "detail": f"Failed to send phone verification: {error_detail or 'Unknown error'}"
            }, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "detail": f"An OTP has been sent to your {otp_type}."
        }

        # If it was sent via a real provider, do not expose the debug_otp in the JSON payload
        if not real_sent:
            response_data["debug_otp"] = otp
            response_data["warning"] = "No active email/SMS provider is configured. Running in demo mode fallback."

        return Response(response_data, status=status.HTTP_200_OK)

class VerifyRegistrationOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_attempt'

    def post(self, request):
        otp_type = request.data.get('type')  # 'email' or 'phone'
        value = request.data.get('value')
        otp = request.data.get('otp')

        if not otp_type or not value or not otp:
            return Response({"detail": "Type, value, and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_type not in ['email', 'phone']:
            return Response({"detail": "Invalid type. Must be 'email' or 'phone'."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_type == 'email':
            value = value.strip().lower()
        else:
            value = value.strip()

        try:
            reg_otp = RegistrationOTP.objects.get(type=otp_type, value=value)
        except RegistrationOTP.DoesNotExist:
            return Response({"detail": "No active OTP verification session found. Please request an OTP first."}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() > reg_otp.expires_at:
            reg_otp.delete()
            return Response({"detail": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        if reg_otp.otp_code != otp:
            return Response({"detail": "Incorrect OTP. Please check the code and try again."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP is correct and valid! Mark as verified
        reg_otp.verified = True
        reg_otp.save()

        return Response({
            "detail": f"{otp_type.capitalize()} verified successfully.",
            "verified": True
        }, status=status.HTTP_200_OK)

class PatientRegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_attempt'

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        phone = request.data.get('phone', '').strip()

        if not email or not phone:
            return Response({"detail": "Email and phone are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify that both email and phone are verified in RegistrationOTP table
        email_verified = RegistrationOTP.objects.filter(type='email', value=email, verified=True).exists()
        phone_verified = RegistrationOTP.objects.filter(type='phone', value=phone, verified=True).exists()

        if not email_verified or not phone_verified:
            return Response({
                "detail": "Both email and phone number must be verified via OTP first."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Email and phone are verified. Proceed with registration.
        serializer = PatientRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = True
            user.save()

            # Clean up verification records
            RegistrationOTP.objects.filter(type='email', value=email).delete()
            RegistrationOTP.objects.filter(type='phone', value=phone).delete()

            # Generate JWT tokens for auto-login
            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "detail": "Patient registered and verified successfully."
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = UserSerializer(user).data
        
        response_data = {"user": user_data}
        
        if user.role == 'PATIENT':
            try:
                patient = user.patient_profile
                patient_data = PatientProfileSerializer(patient).data
                response_data["profile"] = patient_data
            except Patient.DoesNotExist:
                response_data["profile"] = None
        elif user.role == 'DOCTOR':
            try:
                doctor = user.doctor_profile
                from doctors.serializers import DoctorSerializer
                doctor_data = DoctorSerializer(doctor).data
                response_data["profile"] = doctor_data
            except Doctor.DoesNotExist:
                response_data["profile"] = None
        
        return Response(response_data, status=status.HTTP_200_OK)

    @transaction.atomic
    def put(self, request):
        user = request.user
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_serializer.save()
        
        response_data = {"user": user_serializer.data}
        
        if user.role == 'PATIENT':
            try:
                patient = user.patient_profile
                profile_serializer = PatientProfileSerializer(patient, data=request.data, partial=True)
                if not profile_serializer.is_valid():
                    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                profile_serializer.save()
                response_data["profile"] = profile_serializer.data
            except Patient.DoesNotExist:
                response_data["profile"] = None
        elif user.role == 'DOCTOR':
            try:
                doctor = user.doctor_profile
                profile_serializer = DoctorProfileUpdateSerializer(doctor, data=request.data, partial=True)
                if not profile_serializer.is_valid():
                    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                profile_serializer.save()
                from doctors.serializers import DoctorSerializer
                response_data["profile"] = DoctorSerializer(doctor).data
            except Doctor.DoesNotExist:
                response_data["profile"] = None
                
        return Response(response_data, status=status.HTTP_200_OK)


class DebugConfigView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users_data = [{"email": u.email, "is_active": u.is_active, "role": u.role} for u in User.objects.all()]

        config_status = {
            "RESEND_API_KEY_configured": bool(getattr(settings, 'RESEND_API_KEY', '')),
            "BREVO_API_KEY_configured": bool(getattr(settings, 'BREVO_API_KEY', '')),
            "EMAIL_HOST_USER_configured": bool(getattr(settings, 'EMAIL_HOST_USER', '')),
            "TWILIO_ACCOUNT_SID_configured": bool(getattr(settings, 'TWILIO_ACCOUNT_SID', '')),
            "FAST2SMS_API_KEY_configured": bool(getattr(settings, 'FAST2SMS_API_KEY', '')),
            "GEMINI_API_KEY_configured": bool(os.getenv('GEMINI_API_KEY', '')),
            "EMAIL_BACKEND": settings.EMAIL_BACKEND,
            "DEBUG": settings.DEBUG,
            "registered_users": users_data,
        }
        return Response(config_status, status=200)
