from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Patient

User = get_user_model()

class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    phone = serializers.CharField(source='user.phone', required=False, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField(source='user.is_active', required=False)
    
    class Meta:
        model = Patient
        fields = (
            'id',
            'full_name',
            'email',
            'phone',
            'age',
            'blood_group',
            'address',
            'emergency_contact',
            'is_active',
            'created_at'
        )

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
        if 'is_active' in user_data:
            user.is_active = user_data['is_active']
        user.save()

        # Update remaining patient fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
