from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

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
from .models import Notification
from .serializer import NotificationSerializer
from django.db import OperationalError
import datetime
from django.db import OperationalError

from .models import JobPosting, JobApplication, Interview, Notification
from registration.models import UserRegistration
from .serializer import JobPostingSerializer, JobApplicationSerializer, InterviewSerializer, NotificationSerializer
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

# --- 6. APPLY FOR JOB API ---
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser]) # 1. Allow File Uploads
def api_apply_job(request):
    try:
        job_id = request.data.get('job_id')
        user_id = request.data.get('user_id')
        
        # 2. Get the new fields
        cover_letter = request.data.get('cover_letter')
        resume = request.data.get('resume') 

        # Validate Data Exists
        if not job_id or not user_id:
            return Response({"error": "Missing Job ID or User ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Get Instances
        job = JobPosting.objects.get(pk=job_id)
        user = UserRegistration.objects.get(pk=user_id)

        # Check for Duplicate
        if JobApplication.objects.filter(job=job, applicant=user).exists():
            return Response({"error": "You have already applied for this job"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Create Application with Resume and Cover Letter
        JobApplication.objects.create(
            job=job,
            applicant=user,
            status='Pending',
            cover_letter=cover_letter, # <--- Added
            resume=resume              # <--- Added
        )
        return Response({"message": "Application submitted successfully"}, status=status.HTTP_201_CREATED)

    except JobPosting.DoesNotExist:
        return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
    except UserRegistration.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in api_apply_job: {str(e)}")
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
        
        # Send a user notification for important status changes
        try:
            if new_status == 'Accepted':
                send_notification(application.applicant, "Application Accepted", f"Congratulations! You've been accepted for {application.job.title}.")
            elif new_status == 'Rejected':
                send_notification(application.applicant, "Application Update", f"Update regarding {application.job.title}: We have decided not to proceed.")
            elif new_status == 'Scheduled':
                send_notification(application.applicant, "Interview Scheduled", f"An interview for {application.job.title} has been scheduled. Check your dashboard for details.")
        except Exception as e:
            print(f"Failed to send notification on status change: {e}")
            
        return Response({"message": f"Application marked as {new_status}"}, status=status.HTTP_200_OK)

    except JobApplication.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

# --- 8. APPLICATION HISTORY API (NEW) ---
@api_view(['GET'])
def application_history(request, user_id):
    try:
        # Filter by applicant_id (which is the foreign key to UserRegistration)
        apps = JobApplication.objects.filter(applicant_id=user_id)
        serializer = JobApplicationSerializer(apps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- HELPER FUNCTION (FIXED) ---
def send_notification(user, title, message):
    # 1. Create the Database Record
    Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        is_read=False  # <--- FIXED: Changed from 'read' to 'is_read'
    )

# --- NOTIFICATION API (GET) ---
@api_view(['GET'])
def api_user_notifications(request, user_id):
    try:
        notifications = Notification.objects.filter(recipient_id=user_id).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    except OperationalError as oe:
        print(f"OperationalError when fetching notifications: {oe}")
        return Response([], status=200)
    except Exception as e:
        print(f"Error in api_user_notifications: {e}")
        return Response({'error': str(e)}, status=500)


# --- HELPER: Create Notification (for testing) ---
@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
def api_create_notification(request):
    try:
        data = request.data
        user_id = data.get('user_id') or data.get('recipient_id')
        title = data.get('title')
        message = data.get('message')

        if not user_id or not title or not message:
            return Response({'error': 'user_id, title and message are required'}, status=400)

        user = get_object_or_404(UserRegistration, pk=user_id)

        notif = Notification.objects.create(recipient=user, title=title, message=message, is_read=False)
        serializer = NotificationSerializer(notif)
        return Response(serializer.data, status=201)
    except Exception as e:
        print(f"Error in api_create_notification: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['DELETE'])
@authentication_classes([])
def api_delete_notification(request, pk):
    try:
        notif = get_object_or_404(Notification, pk=pk)
        notif.delete()
        return Response({'message': 'Notification deleted', 'id': pk}, status=200)
    except Exception as e:
        print(f"Error deleting notification {pk}: {e}")
        return Response({'error': str(e)}, status=500)


# --- MARK NOTIFICATION READ ---
@api_view(['POST'])
@authentication_classes([])
def api_mark_notification_read(request, pk):
    try:
        notif = get_object_or_404(Notification, pk=pk)
        notif.is_read = True
        notif.save()
        return Response({'message': 'Marked as read', 'id': notif.id})
    except Exception as e:
        print(f"Error marking notification read: {e}")
        return Response({'error': str(e)}, status=500)

# --- INTERVIEW LOGIC (API) ---

@api_view(['GET'])
def api_interview_list(request):
    try:
        interviews = Interview.objects.filter(status='Scheduled').order_by('date_time')
        serializer = InterviewSerializer(interviews, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# --- 1. DRF VERSION (Renamed to avoid conflict) ---
@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
def api_interview_create(request): # Renamed from interview_create
    try:
        data = request.data
        app_id = data.get('application_id')
        application = get_object_or_404(JobApplication, id=app_id)

        date_part = data.get('date')
        time_part = data.get('time')
        location = data.get('location') or 'Online'

        if not date_part or not time_part:
            return Response({"error": "Date and Time are required"}, status=400)

        parsed_dt = datetime.datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")

        Interview.objects.create(
            application=application,
            date_time=parsed_dt,
            location=location,
            status='Scheduled'
        )

        application.status = "Interviewing"
        application.save()

        # 🔥 NOTIFICATION 🔥
        send_notification(
            user=application.applicant,
            title="Interview Scheduled",
            message=f"Interview for {application.job.title} scheduled: {parsed_dt.strftime('%b %d, %H:%M')}."
        )

        return Response({"message": "Interview Scheduled Successfully"}, status=201)

    except Exception as e:
        print("Error scheduling interview:", str(e))
        return Response({"error": str(e)}, status=400)

# ---- DELETE INTERVIEW VIEW ----
@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([])
def delete_interview(request, pk):
    try:
        interview = Interview.objects.get(pk=pk)
        interview.delete()
        return Response({'message': 'Interview deleted'}, status=200)
    except Interview.DoesNotExist:
        return Response({'error': 'Interview not found'}, status=404)

# --- 2. PLAIN DJANGO VERSION (Fallback) ---
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
        # Create Interview
        Interview.objects.create(
            application=application,
            date_time=parsed_dt,
            location=location,
            status='Scheduled'
        )
        
        # Update Application Status
        application.status = 'Interviewing'
        application.save()

        # 🔥 TRIGGER NOTIFICATION (Fixed is_read inside helper) 🔥
        send_notification(
            user=application.applicant,
            title="Interview Scheduled",
            message=f"Good news! An interview for {application.job.title} has been scheduled on {parsed_dt.strftime('%b %d, %I:%M %p')} at {location}."
        )

        # Serialize created interview
        interview = Interview.objects.filter(application=application, date_time=parsed_dt).order_by('-id').first()
        try:
            from .serializer import InterviewSerializer
            serialized = InterviewSerializer(interview).data if interview else {'message': 'Interview Scheduled Successfully'}
        except Exception:
            serialized = {'message': 'Interview Scheduled Successfully'}
        
        return JsonResponse(serialized, status=201, safe=False)

    except Exception as e:
        print('Error saving interview (no csrf view):', str(e))
        return JsonResponse({'error': str(e)}, status=500)


# --- REVIEW APPLICATION VIEW (API) ---
@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
def api_review_application(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    action = request.data.get('action')
    job = application.job 

    if action == 'accept':
        # --- 1. Check if slots are available ---
        if job.slots <= 0:
            return Response({"error": "Cannot accept. This job has 0 slots remaining."}, status=400)

        # --- 2. Deduct the slot ---
        job.slots -= 1

        # --- 3. Close job if slots hit 0 ---
        if job.slots == 0:
            job.status = 'Closed'
        
        job.save()

        # --- 4. Update Application Status ---
        application.status = 'Accepted'
        application.save()

        # 🔥 NOTIFICATION 🔥
        send_notification(application.applicant, "Application Accepted", f"Congratulations! You've been accepted for {application.job.title}.")
        
        return Response({
            "message": "Application Accepted and slot deducted.", 
            "status": "Accepted",
            "slots_remaining": job.slots
        })
    
    elif action == 'reject':
        application.status = 'Rejected'
        application.save()
        
        # 🔥 NOTIFICATION 🔥
        send_notification(application.applicant, "Application Update", f"Update regarding {application.job.title}: We have decided not to proceed.")
        
        return Response({"message": "Application Rejected.", "status": "Rejected"})
    
    return Response({"error": "Invalid action provided"}, status=400)


# ==========================================
#  DELETE APPLICATION API
@csrf_exempt    
@api_view(['DELETE'])
@authentication_classes([])
def delete_application(request, pk):
    try:
        application = JobApplication.objects.get(pk=pk)
        application.delete()
        return Response({'message': 'Application deleted successfully'}, status=200)

    except JobApplication.DoesNotExist:
        return Response({'error': 'Application not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

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
    if not request.session.get('user_id'):
        return redirect('registration:login_view')
    tasks = JobApplication.objects.filter(status='Pending').order_by('-applied_at')
    return render(request, 'dashboard/tasks.html', {'tasks': tasks})

def system_settings(request):
    return render(request, 'dashboard/settings.html')

def interview_list(request):
    interviews = Interview.objects.select_related('application__applicant', 'application__job').all().order_by('date_time')
    return render(request, 'interviews/list.html', {'interviews': interviews})

# Note: This is your HTML view logic for interview creation (likely used by web forms)
def interview_create(request, application_id):
    return redirect('jobs:interview_list')

def review_application(request, pk):
    return redirect('jobs:application_list')