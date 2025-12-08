from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from job_recruitmentapp.models import JobPosting, JobApplication
from registration.models import UserRegistration

# --- NEW IMPORTS FOR API ---
from rest_framework import viewsets, permissions, parsers
from registration.serializer import UserSerializer

# =========================================
#  WEBSITE VIEWS (HTML) - Keep these!
# =========================================

def user_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('registration:login_view')

    try:
        jobs = JobPosting.objects.filter(status='Open')
        applied_job_ids = JobApplication.objects.filter(applicant_id=user_id).values_list('job_id', flat=True)
        user = UserRegistration.objects.get(id=user_id)
    except:
        jobs = []
        applied_job_ids = []
        user = None
     
    context = {
        'current_user': request.session.get('user_name', 'Guest'),
        'user_obj': user,
        'jobs': jobs,
        'jobs_count': len(jobs),
        'applied_job_ids': applied_job_ids
    }
    return render(request, 'user/userdashboard.html', context)

def user_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('registration:login_view')
    user = get_object_or_404(UserRegistration, id=user_id)
    return render(request, 'user/profile.html', {'user': user})

def user_profile_edit(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('registration:login_view')
    
    user = get_object_or_404(UserRegistration, id=user_id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone_number = request.POST.get('phone_number')
        user.address = request.POST.get('address')
        user.bio = request.POST.get('bio')
        user.skills = request.POST.get('skills')

        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES.get('profile_picture')
        if request.FILES.get('resume'):
            user.resume = request.FILES.get('resume')

        user.save()
        messages.success(request, "Profile updated!")
        return redirect('userapp:user_profile')

    return render(request, 'user/edit_profile.html', {'user': user})

def apply_for_job(request, job_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('registration:login_view')

    user = get_object_or_404(UserRegistration, id=user_id)
    job = get_object_or_404(JobPosting, id=job_id)

    if JobApplication.objects.filter(applicant=user, job=job).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('userapp:user_dashboard')

    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter')
        resume = request.FILES.get('resume')

        if not resume and user.resume:
            resume = user.resume
        elif not resume and not user.resume:
            messages.error(request, "Please upload a resume to apply.")
            return render(request, 'user/application_form.html', {'job': job, 'user': user})

        JobApplication.objects.create(
            applicant=user, 
            job=job,
            cover_letter=cover_letter,
            resume=resume
        )
        messages.success(request, f"Application submitted for {job.title}!")
        return redirect('userapp:user_dashboard')

    return render(request, 'user/application_form.html', {'job': job, 'user': user})


# =========================================
#  API VIEWS (JSON) - React Native connects here!
# =========================================

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserRegistration.objects.all()
    serializer_class = UserSerializer
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser) # Needed for Image Uploads