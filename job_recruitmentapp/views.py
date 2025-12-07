from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from .models import JobPosting, JobApplication
from registration.models import UserRegistration
from .serializer import JobPostingSerializer, JobApplicationSerializer
from registration.serializer import UserSerializer
from .models import Interview
from .serializer import InterviewSerializer
import datetime

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

# --- 6. APPLY FOR JOB API ---
# views.py

@api_view(['POST'])
def api_apply_job(request):
    try:
        job_id = request.data.get('job_id')
        user_id = request.data.get('user_id')

        # 1. Validate Data Exists
        if not job_id or not user_id:
            return Response({"error": "Missing Job ID or User ID"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Get Instances
        job = JobPosting.objects.get(pk=job_id)
        user = UserRegistration.objects.get(pk=user_id)

        # 3. Check for Duplicate
        if JobApplication.objects.filter(job=job, applicant=user).exists():
            # This is the 400 error you were seeing (which is good!)
            return Response({"error": "You have already applied for this job"}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Create Application
        JobApplication.objects.create(
            job=job,
            applicant=user,
            status='Pending'
        )
        return Response({"message": "Application submitted successfully"}, status=status.HTTP_201_CREATED)

    except JobPosting.DoesNotExist:
        return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
    except UserRegistration.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in api_apply_job: {str(e)}") # Print error to terminal for debugging
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

# --- 7. UPDATE APPLICATION STATUS API ---
@api_view(['PUT'])
def api_update_application_status(request, pk):
    try:
        application = JobApplication.objects.get(pk=pk)
        new_status = request.data.get('status')
        
        if new_status not in ['Accepted', 'Rejected', 'Scheduled', 'Pending']:
             return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        application.status = new_status
        application.save()
        return Response({"message": f"Application marked as {new_status}"}, status=status.HTTP_200_OK)

    except JobApplication.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
    

# --- INTERVIEW LOGIC (API) ---

@api_view(['GET'])
def api_interview_list(request):
    try:
        # LOGIC: Filter Scheduled interviews
        interviews = Interview.objects.filter(status='Scheduled').order_by('date_time')
        
        # API CHANGE: Serialize data to JSON instead of rendering HTML
        serializer = InterviewSerializer(interviews, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
def interview_create(request):
    """
    Creates an interview.
    Expects JSON body: 
    { 
        "application_id": 1,
        "date": "2025-12-30", 
        "time": "14:30", 
        "location": "Zoom" 
    }
    """
    try:
        data = request.data
        
        # 1. Get the Application
        app_id = data.get('application_id')
        application = get_object_or_404(JobApplication, id=app_id)

        # 2. Combine Date and Time strings into one DateTime
        date_part = data.get('date')
        time_part = data.get('time')
        location = data.get('location') or 'Online'

        if not date_part or not time_part:
            return Response({"error": "Date and Time are required"}, status=400)

        # Expecting formats: YYYY-MM-DD and HH:MM (24-hour)
        try:
            parsed_dt = datetime.datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
        except Exception as e:
            return Response({"error": "Invalid date/time format. Use YYYY-MM-DD and HH:MM."}, status=400)

        # 3. Create the Interview Object
        try:
            Interview.objects.create(
                application=application,
                date_time=parsed_dt,
                location=location,
                status='Scheduled'
            )

            # 4. Update Application Status
            application.status = "Interviewing"
            application.save()

            return Response({"message": "Interview Scheduled Successfully"}, status=201)
        except Exception as e:
            print("Error saving interview:", str(e))
            return Response({"error": str(e)}, status=500)

    except Exception as e:
        print("Error scheduling interview:", str(e))
        return Response({"error": str(e)}, status=400)


# A plain Django view (not DRF) that is explicitly CSRF-exempt and returns
# JsonResponse. Some environments (DRF decorators + middleware) still
# result in CSRF checks; to be robust for mobile clients we'll expose this
# endpoint and point the frontend to it. It mirrors the logic of
# interview_create but uses plain Django request handling.
@csrf_exempt
def interview_create_no_csrf(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    app_id = data.get('application_id')
    date_part = data.get('date')
    time_part = data.get('time')
    location = data.get('location') or 'Online'

    if not app_id or not date_part or not time_part:
        return JsonResponse({'error': 'application_id, date and time are required'}, status=400)

    try:
        application = get_object_or_404(JobApplication, id=app_id)
    except Exception:
        return JsonResponse({'error': 'Application not found'}, status=404)

    # Parse datetime
    try:
        parsed_dt = datetime.datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
    except Exception:
        return JsonResponse({'error': 'Invalid date/time format. Use YYYY-MM-DD and HH:MM.'}, status=400)

    try:
        Interview.objects.create(
            application=application,
            date_time=parsed_dt,
            location=location,
            status='Scheduled'
        )
        application.status = 'Interviewing'
        application.save()
        # Serialize created interview and return it so clients can update UI immediately
        interview = Interview.objects.filter(application=application, date_time=parsed_dt).order_by('-id').first()
        try:
            from .serializer import InterviewSerializer
            serialized = InterviewSerializer(interview).data if interview else {'message': 'Interview Scheduled Successfully'}
        except Exception:
            serialized = {'message': 'Interview Scheduled Successfully'}
        return JsonResponse(serialized, status=201)
    except Exception as e:
        print('Error saving interview (no csrf view):', str(e))
        return JsonResponse({'error': str(e)}, status=500)


# --- REVIEW APPLICATION VIEW (API) ---

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
def api_review_application(request, pk):
    """
    API Version of your review logic.
    Expects JSON: { "action": "accept" } or { "action": "reject" }
    """
    application = get_object_or_404(JobApplication, pk=pk)

    # API CHANGE: Get 'action' from JSON body
    action = request.data.get('action')
    
    if action == 'accept':
        application.status = 'Accepted'
        application.save()
        return Response({"message": "Application Accepted.", "status": "Accepted"})
    
    elif action == 'reject':
        application.status = 'Rejected'
        application.save()
        return Response({"message": "Application Rejected.", "status": "Rejected"})
    
    return Response({"error": "Invalid action provided"}, status=400)
   
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
    # Ensure admin / HR is logged in (uses same session system as other HTML views)
    if not request.session.get('user_id'):
        return redirect('registration:login_view')

    # Provide list of pending job applications to the template
    tasks = JobApplication.objects.filter(status='Pending').order_by('-applied_at')
    return render(request, 'dashboard/tasks.html', {'tasks': tasks})

def system_settings(request):
    return render(request, 'dashboard/settings.html')

def interview_list(request):
    # Render HTML list of interviews for admin panel
    interviews = Interview.objects.select_related('application__applicant', 'application__job').all().order_by('date_time')
    return render(request, 'interviews/list.html', {'interviews': interviews})

def interview_create(request, application_id):
    return redirect('jobs:interview_list')

def review_application(request, pk):
    return redirect('jobs:application_list')