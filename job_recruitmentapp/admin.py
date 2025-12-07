from django.contrib import admin
from .models import JobPosting
from .models import JobApplication
from .models import Interview

# Register your models here.

admin.site.register(JobPosting)
admin.site.register(JobApplication)
admin.site.register(Interview)