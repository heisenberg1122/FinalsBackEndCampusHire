from rest_framework import serializers
from .models import Interview, JobPosting, JobApplication, Interview, Notification
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

class InterviewSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    job_title = serializers.CharField(source='application.job.title', read_only=True)
    application_id = serializers.PrimaryKeyRelatedField(read_only=True, source='application')

    class Meta:
        model = Interview
        fields = ['id', 'application_id', 'applicant_name', 'job_title', 'date_time', 'location', 'notes', 'status']

    def get_applicant_name(self, obj):
        # Safe way to get full name (First + Last)
        if obj.application and obj.application.applicant:
            return f"{obj.application.applicant.first_name} {obj.application.applicant.last_name}"
        return "Unknown Applicant"

class NotificationSerializer(serializers.ModelSerializer):
    # Provide both 'is_read' (model) and 'read' alias for frontend compatibility
    read = serializers.BooleanField(source='is_read', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'read', 'created_at']