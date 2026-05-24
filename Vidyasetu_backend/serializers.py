from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # first_name will map to the user's display name
        fields = ['id', 'username', 'email', 'password', 'role', 'department', 'roll_no', 'first_name']
        extra_kwargs = {'password': {'write_only': True}} # Never return the password in responses

    def create(self, validated_data):
        # create_user automatically hashes the password
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'student'),
            department=validated_data.get('department', ''),
            roll_no=validated_data.get('roll_no', ''),
            first_name=validated_data.get('first_name', '')
        )
        return user