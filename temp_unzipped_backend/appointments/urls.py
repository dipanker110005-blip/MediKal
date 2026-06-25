from django.urls import path
from .views import AppointmentListCreateView, AppointmentDetailView, RazorpayConfigView, VerifyPaymentView

urlpatterns = [
    path('', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('config/', RazorpayConfigView.as_view(), name='razorpay-config'),
    path('<int:pk>/verify_payment/', VerifyPaymentView.as_view(), name='verify-payment'),
]
