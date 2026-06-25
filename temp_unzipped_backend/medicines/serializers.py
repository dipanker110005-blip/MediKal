from rest_framework import serializers
from .models import Prescription, MedicineOrder
from patients.models import Patient
from doctors.serializers import DoctorSerializer

class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    doctor_detail = DoctorSerializer(source='doctor', read_only=True)

    class Meta:
        model = Prescription
        fields = ('id', 'patient', 'patient_name', 'doctor', 'doctor_detail', 'image', 'notes', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_patient(self, value):
        # Ensure that the patient belongs to the request user if it's a patient request
        request = self.context.get('request')
        if request and hasattr(request.user, 'patient_profile'):
            if value != request.user.patient_profile:
                raise serializers.ValidationError("You cannot create a prescription upload for another patient.")
        return value

class MedicineOrderSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    prescription_detail = PrescriptionSerializer(source='prescription', read_only=True)

    class Meta:
        model = MedicineOrder
        fields = (
            'id',
            'patient',
            'patient_name',
            'prescription',
            'prescription_detail',
            'delivery_address',
            'contact_number',
            'status',
            'total_price',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'status', 'total_price', 'created_at', 'updated_at')

    def validate_patient(self, value):
        request = self.context.get('request')
        if request and hasattr(request.user, 'patient_profile'):
            if value != request.user.patient_profile:
                raise serializers.ValidationError("You cannot place a medicine order for another patient.")
        return value
