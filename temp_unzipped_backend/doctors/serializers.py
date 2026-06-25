from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Doctor

User = get_user_model()

class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    
    class Meta:
        model = Doctor
        fields = (
            'id', 
            'full_name', 
            'email', 
            'phone', 
            'specialization', 
            'qualification', 
            'experience', 
            'consultation_fee', 
            'bio', 
            'profile_image', 
            'online_status', 
            'rating',
            'verification_status'
        )
        read_only_fields = ('id', 'online_status', 'rating')

class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = (
            'specialization',
            'qualification',
            'experience',
            'consultation_fee',
            'bio',
            'profile_image',
            'online_status'
        )

class DoctorVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'verification_status')

class DoctorCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default='')
    password = serializers.CharField(write_only=True, min_length=6)
    specialization = serializers.ChoiceField(choices=Doctor.SPECIALIZATION_CHOICES)
    qualification = serializers.CharField(max_length=100)
    experience = serializers.IntegerField(min_value=0)
    consultation_fee = serializers.DecimalField(max_digits=8, decimal_places=2)
    bio = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.pop('email')
        full_name = validated_data.pop('full_name')
        phone = validated_data.pop('phone', '')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            email=email,
            full_name=full_name,
            phone=phone,
            password=password,
            role='DOCTOR',
            is_active=True
        )

        doctor = Doctor.objects.create(
            user=user,
            verification_status='APPROVED',  # Admins approve immediately
            **validated_data
        )
        return doctor

class DoctorAdminUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    phone = serializers.CharField(source='user.phone', required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Doctor
        fields = (
            'id', 
            'full_name', 
            'email', 
            'phone', 
            'specialization', 
            'qualification', 
            'experience', 
            'consultation_fee', 
            'bio', 
            'profile_image', 
            'verification_status',
            'online_status', 
            'rating'
        )
        read_only_fields = ('id', 'rating')

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        if 'email' in user_data:
            email = user_data['email'].lower()
            if User.objects.exclude(id=user.id).filter(email=email).exists():
                raise serializers.ValidationError({"email": "A user with this email already exists."})
            user.email = email
        if 'full_name' in user_data:
            user.full_name = user_data['full_name']
        if 'phone' in user_data:
            user.phone = user_data['phone']
        user.save()

        # Update remaining doctor fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
