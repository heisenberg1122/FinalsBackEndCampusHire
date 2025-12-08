from django.db import models


class UserRegistration(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Applicant', 'Applicant'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    gender = models.CharField(max_length=12)
    password = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Applicant')

    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    # --- NEW FIELDS FOR PROFILE SETUP ---
    bio = models.TextField(blank=True, null=True, help_text="About User")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    skills = models.CharField(max_length=255, blank=True, null=True, help_text="Comma separated e.g. Python, Java")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
