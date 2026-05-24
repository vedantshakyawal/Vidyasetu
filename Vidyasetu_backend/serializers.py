# Vidyasetu_backend/serializers.py
from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 
            'role', 'department', 'roll_no', 'student_class', 
            'course', 'device_id'
        ]
        # Ensure password is never returned in API responses
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Create user instance
        user = super().create(validated_data)
        # Hash the password properly
        if password:
            user.set_password(password)
            user.save()
        return user