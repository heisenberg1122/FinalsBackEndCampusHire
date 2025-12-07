from rest_framework import serializers
from .models import JobPosting, JobApplication
from registration.models import UserRegistration
# Fix import to use registration.serializers
from registration.serializer import UserSerializer 

class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = '__all__'

class JobApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    job = JobPostingSerializer(read_only=True)
    class Meta:
        model = JobApplication
        fields = '__all__'