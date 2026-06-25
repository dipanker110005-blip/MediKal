from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from patients.models import Patient

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'phone', 'role', 'created_at')
        read_only_fields = ('id', 'role', 'created_at')

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('age', 'blood_group', 'address', 'emergency_contact')

class PatientRegisterSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(required=True)
    blood_group = serializers.ChoiceField(choices=Patient.BLOOD_GROUP_CHOICES, required=True)
    address = serializers.CharField(required=False, allow_blank=True, default='')
    emergency_contact = serializers.CharField(required=False, allow_blank=True, default='')
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'password', 'age', 'blood_group', 'address', 'emergency_contact')

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email, is_active=True).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data['email']
        
        # Delete existing inactive user if they are trying to register again
        User.objects.filter(email=email, is_active=False).delete()
        
        age = validated_data.pop('age')
        blood_group = validated_data.pop('blood_group')
        address = validated_data.pop('address', '')
        emergency_contact = validated_data.pop('emergency_contact', '')
        password = validated_data.pop('password')

        # Create user (set is_active=True)
        user = User.objects.create_user(
            email=email,
            full_name=validated_data['full_name'],
            phone=validated_data.get('phone', ''),
            password=password,
            role='PATIENT',
            is_active=True
        )

        # Create linked patient profile
        Patient.objects.create(
            user=user,
            age=age,
            blood_group=blood_group,
            address=address,
            emergency_contact=emergency_contact
        )

        return user
