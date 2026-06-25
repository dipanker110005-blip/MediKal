from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import PatientRegisterView, CustomLoginView, SendRegistrationOTPView, VerifyRegistrationOTPView, UserProfileView, DebugConfigView

urlpatterns = [
    path('register/patient/', PatientRegisterView.as_view(), name='patient-register'),
    path('register/send-otp/', SendRegistrationOTPView.as_view(), name='register-send-otp'),
    path('register/verify-otp/', VerifyRegistrationOTPView.as_view(), name='register-verify-otp'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('debug-config/', DebugConfigView.as_view(), name='debug-config'),
]
