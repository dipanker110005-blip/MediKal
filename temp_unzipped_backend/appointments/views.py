import os
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer
from patients.models import Patient
from doctors.models import Doctor

class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    API view to list appointments or create a new booking.
    Supports role-based filtering:
    - Patients see their own appointments.
    - Doctors see appointments booked with them.
    - Admins see all appointments.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            try:
                patient = user.patient_profile
                return Appointment.objects.filter(patient=patient).order_by('-date', '-time')
            except Patient.DoesNotExist:
                return Appointment.objects.none()
        elif user.role == 'DOCTOR':
            try:
                doctor = user.doctor_profile
                return Appointment.objects.filter(doctor=doctor).order_by('-date', '-time')
            except Doctor.DoesNotExist:
                return Appointment.objects.none()
        elif user.role == 'ADMIN':
            return Appointment.objects.all().order_by('-date', '-time')
        return Appointment.objects.none()

    def perform_create(self, serializer):
        appointment = serializer.save()
        try:
            from notifications.utils import send_notification
            # Notify Patient
            send_notification(
                user=appointment.patient.user,
                title="Appointment Booked!",
                body=f"Your appointment with Dr. {appointment.doctor.user.full_name} is scheduled for {appointment.date} at {appointment.time}."
            )
            # Notify Doctor
            send_notification(
                user=appointment.doctor.user,
                title="New Consultation Booked",
                body=f"Patient {appointment.patient.user.full_name} has booked an appointment for {appointment.date} at {appointment.time}."
            )
        except Exception as e:
            print(f"Failed to trigger booking notifications: {e}")

class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to view details of a specific appointment, update its status, or delete it.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        appointment = serializer.save()
        try:
            from notifications.utils import send_notification
            status = appointment.status
            if status == 'COMPLETED':
                send_notification(
                    user=appointment.patient.user,
                    title="Consultation Completed",
                    body=f"Your consultation session with Dr. {appointment.doctor.user.full_name} has been marked as completed."
                )
            elif status == 'CANCELLED':
                send_notification(
                    user=appointment.patient.user,
                    title="Consultation Cancelled",
                    body=f"Your appointment with Dr. {appointment.doctor.user.full_name} has been cancelled."
                )
                send_notification(
                    user=appointment.doctor.user,
                    title="Consultation Cancelled",
                    body=f"Your scheduled consultation with patient {appointment.patient.user.full_name} has been cancelled."
                )
        except Exception as e:
            print(f"Failed to trigger update notifications: {e}")

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return Appointment.objects.filter(patient__user=user)
        elif user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__user=user)
        elif user.role == 'ADMIN':
            return Appointment.objects.all()
        return Appointment.objects.none()



from rest_framework.views import APIView

class RazorpayConfigView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        import os
        return Response({
            'key_id': os.getenv('RAZORPAY_KEY_ID', '')
        })

class VerifyPaymentView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk, patient__user=request.user)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
            
        payment_id = request.data.get('razorpay_payment_id')
        signature = request.data.get('razorpay_signature')
        
        if not payment_id or not signature:
            return Response({'detail': 'payment_id and signature are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        order_id = appointment.razorpay_order_id
        
        verified = False
        if not key_secret:
            # Sandbox mock verification
            print(f"[RAZORPAY SANDBOX] Mock verifying payment {payment_id} for order {order_id}")
            verified = True
        else:
            # Real HMAC verification
            import hmac
            import hashlib
            msg = f"{order_id}|{payment_id}"
            generated_signature = hmac.new(
                key=key_secret.encode('utf-8'),
                msg=msg.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            verified = (generated_signature == signature)
            
        if verified:
            appointment.status = 'CONFIRMED'
            appointment.razorpay_payment_id = payment_id
            appointment.razorpay_signature = signature
            appointment.save()
            
            # Trigger notifications
            try:
                from notifications.utils import send_notification
                send_notification(
                    user=appointment.patient.user,
                    title="Appointment Booked & Confirmed!",
                    body=f"Your appointment with Dr. {appointment.doctor.user.full_name} is confirmed for {appointment.date} at {appointment.time}."
                )
                send_notification(
                    user=appointment.doctor.user,
                    title="New Consultation Booked",
                    body=f"Patient {appointment.patient.user.full_name} has booked an appointment for {appointment.date} at {appointment.time}."
                )
            except Exception as e:
                print(f"Failed to trigger booking notifications: {e}")
                
            return Response({'status': 'success', 'message': 'Payment verified and booking confirmed.'})
        else:
            return Response({'detail': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
