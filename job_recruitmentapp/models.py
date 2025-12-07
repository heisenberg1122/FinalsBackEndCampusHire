from django.conf import settings
from django.db import models

class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    job_position = models.CharField(max_length=100)
    slots = models.IntegerField()
    status = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    applicant = models.ForeignKey('registration.UserRegistration', on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    
    # --- APPLICATION DETAILS ---
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    cover_letter = models.TextField(blank=True, null=True) # New field for "Fill up something"
    
    status = models.CharField(max_length=50, default='Pending') 
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.first_name} applied for {self.job.title}"

class Interview(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Scheduled')

    def __str__(self):
        return f"Interview: {self.application.applicant.first_name}"

# --- NEW: NOTIFICATION MODEL ---
class Notification(models.Model):
    # Link to your custom user model
    recipient = models.ForeignKey('registration.UserRegistration', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient}: {self.title}"