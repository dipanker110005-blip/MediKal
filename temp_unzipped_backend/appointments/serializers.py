import urllib.request
import urllib.parse
import json
import os
import decimal
import base64
from rest_framework import serializers
from doctors.models import Doctor
from patients.models import Patient
from .models import Appointment

def create_razorpay_order(amount_paisa, appointment_id):
    key_id = os.getenv('RAZORPAY_KEY_ID')
    key_secret = os.getenv('RAZORPAY_KEY_SECRET')
    
    if not key_id or not key_secret:
        print("[RAZORPAY SANDBOX] Keys not set. Simulating Razorpay order.")
        return f"order_mock_{appointment_id}", True, None
        
    url = "https://api.razorpay.com/v1/orders"
    data = json.dumps({
        'amount': amount_paisa,
        'currency': 'INR',
        'receipt': f"receipt_apt_{appointment_id}",
    }).encode('utf-8')
    
    auth_str = f"{key_id}:{key_secret}"
    auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    
    req = urllib.request.Request(url, data=data)
    req.add_header('Authorization', f'Basic {auth_b64}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data.get('id'), True, None
    except Exception as e:
        if hasattr(e, 'read'):
            err_msg = e.read().decode('utf-8')
            try:
                err_json = json.loads(err_msg)
                return None, False, err_json.get('error', {}).get('description', str(e))
            except:
                pass
        return None, False, str(e)

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = (
            'id', 
            'doctor', 
            'doctor_name', 
            'doctor_specialization', 
            'patient_name', 
            'date', 
            'time', 
            'consultation_type', 
            'status', 
            'referral_code', 
            'total_fee',
            'razorpay_order_id',
            'razorpay_payment_id',
            'razorpay_signature'
        )
        read_only_fields = ('id', 'total_fee', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')

    def validate(self, data):
        # If updating (PATCH/PUT)
        if self.instance is not None:
            # Ensure only status is allowed to be updated
            allowed_update_fields = {'status'}
            modified_fields = set(data.keys()) - allowed_update_fields
            if modified_fields:
                raise serializers.ValidationError("Only status can be updated after booking.")
            
            # Validate status choice
            status = data.get('status')
            if status and status not in ['CANCELLED', 'CONFIRMED', 'COMPLETED']:
                raise serializers.ValidationError("Invalid status transition.")
            return data

        # If creating (POST)
        doctor = data.get('doctor')
        if not doctor:
            raise serializers.ValidationError("Doctor is required.")
            
        referral_code = data.get('referral_code')
        if referral_code and referral_code.upper() != 'MEDIKAL20':
            raise serializers.ValidationError({"referral_code": "Invalid referral discount code."})
            
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("User authentication required.")
            
        try:
            patient = request.user.patient_profile
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Only patients can book appointments.")

        doctor = validated_data['doctor']
        base_fee = doctor.consultation_fee
        referral_code = validated_data.get('referral_code', '')
        
        # Apply referral discount logic
        total_fee = base_fee
        if referral_code and referral_code.upper() == 'MEDIKAL20':
            total_fee = base_fee * decimal_discount()

        # Create PENDING appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=validated_data['date'],
            time=validated_data['time'],
            consultation_type=validated_data.get('consultation_type', 'ONLINE'),
            referral_code=referral_code,
            total_fee=total_fee,
            status='PENDING'
        )

        # Call Razorpay to generate order
        amount_paisa = int(total_fee * 100)
        order_id, success, error_message = create_razorpay_order(amount_paisa, appointment.id)
        if not success:
            appointment.delete()
            raise serializers.ValidationError({"detail": f"Razorpay Order generation failed: {error_message}"})
            
        appointment.razorpay_order_id = order_id
        appointment.save()
        return appointment

# Helper method to represent decimals in calculations
def decimal_discount():
    return decimal.Decimal('0.8')
