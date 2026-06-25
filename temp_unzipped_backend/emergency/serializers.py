from rest_framework import serializers
from patients.models import Patient
from .models import EmergencyRequest

class EmergencyRequestSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    phone = serializers.CharField(source='patient.user.phone', read_only=True)

    class Meta:
        model = EmergencyRequest
        fields = ('id', 'patient_name', 'phone', 'latitude', 'longitude', 'status', 'created_at')
        read_only_fields = ('id', 'status', 'created_at')

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")
            
        try:
            patient = request.user.patient_profile
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Only patients can submit emergency dispatches.")

        emergency = EmergencyRequest.objects.create(
            patient=patient,
            latitude=validated_data['latitude'],
            longitude=validated_data['longitude'],
            status='PENDING'
        )
        return emergency
