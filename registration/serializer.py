from rest_framework import serializers
from .models import UserRegistration

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        fields = '__all__'

# --- THIS WAS MISSING ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        # Fields to send to the frontend
        fields = ['id', 'first_name', 'last_name', 'email', 'role', 'gender', 'profile_picture', 'bio', 'resume', 'phone_number', 'address', 'skills']