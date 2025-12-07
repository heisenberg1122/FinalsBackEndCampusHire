from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import JobPosting, JobApplication
from registration.models import UserRegistration
from .serializer import JobPostingSerializer, JobApplicationSerializer
from registration.serializer import UserSerializer

# ==========================================
#  API VIEWS (Mobile / React Native)
# ==========================================

# --- 1. LOGIN API ---
@api_view(['POST'])
def api_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    try:
        user = UserRegistration.objects.get(email=email)
        if user.password == password: 
            return Response({
                "message": "Login successful",
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
    except UserRegistration.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

# --- 2. DASHBOARD STATS ---
@api_view(['GET'])
def api_dashboard_stats(request):
    data = {
        "total_jobs": JobPosting.objects.count(),
        "total_users": UserRegistration.objects.count(),
        "total_applications": JobApplication.objects.count(),
        "pending_tasks": JobApplication.objects.filter(status='Pending').count()
    }
    return Response(data)

# --- 3. JOB LIST & CREATE ---
@api_view(['GET', 'POST'])
def api_jobs(request):
    if request.method == 'GET':
        jobs = JobPosting.objects.all().order_by('-id') # Show newest first
        serializer = JobPostingSerializer(jobs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = JobPostingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 4. JOB DETAIL (EDIT & DELETE) ---
@api_view(['GET', 'PUT', 'DELETE'])
def api_job_detail(request, pk):
    try:
        job = JobPosting.objects.get(pk=pk)
    except JobPosting.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = JobPostingSerializer(job)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = JobPostingSerializer(job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- 5. APPLICATIONS API ---
@api_view(['GET'])
def api_applications(request):
    apps = JobApplication.objects.all()
    serializer = JobApplicationSerializer(apps, many=True)
    return Response(serializer.data)


# ==========================================
#  HTML VIEWS (Desktop / Admin Panel)
# ==========================================

def admin_dashboard_view(request):
    if not request.session.get('user_id'):
        return redirect('registration:login_view')
    context = {
        'current_user': request.session.get('user_name', 'Admin'),
        'total_jobs': JobPosting.objects.count(),
        'total_users': UserRegistration.objects.count(),
        'total_applications': JobApplication.objects.count(),
        'pending_tasks': JobApplication.objects.filter(status='Pending').count(),
    }
    return render(request, 'admindashboard.html', context)

def jobs_html(request):
    jobs = JobPosting.objects.all()
    return render(request, 'jobs/list.html', {'jobs': jobs})

def job_create_html(request):
    if request.method == 'POST':
        JobPosting.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            job_position=request.POST.get('job_position'),
            slots=request.POST.get('slots'),
            status='Open',
            salary=request.POST.get('salary')
        )
        return redirect('jobs:jobs_html')
    return render(request, 'jobs/form.html')

def job_update_html(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.save()
        return redirect('jobs:jobs_html')
    return render(request, 'jobs/form.html', {'job': job})

def job_delete_html(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        job.delete()
        return redirect('jobs:jobs_html')
    return render(request, 'jobs/delete.html', {'job': job})

def application_list(request):
    return render(request, 'dashboard/applications.html')

def pending_tasks(request):
    return render(request, 'dashboard/tasks.html')

def system_settings(request):
    return render(request, 'dashboard/settings.html')

def interview_list(request):
    return render(request, 'interviews/list.html')

def interview_create(request, application_id):
    return redirect('jobs:interview_list')

def review_application(request, pk):
    return redirect('jobs:application_list')