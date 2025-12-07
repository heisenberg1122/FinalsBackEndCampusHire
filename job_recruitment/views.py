from django.shortcuts import render, redirect
# Safe imports
try:
    from job_recruitmentapp.models import JobPosting, JobApplication
    from registration.models import UserRegistration
except ImportError:
    pass

def homepage_view(request):
    return render(request, 'homepage.html')

def admin_dashboard_view(request):
    # 1. Check Login
    if not request.session.get('user_id'):
        return redirect('registration:login_view')

    # 2. Check Role (Security Check)
    if request.session.get('role') != 'Admin':
        return redirect('userapp:user_dashboard') 

    # 3. Fetch Data
    try:
        total_jobs = JobPosting.objects.count()
        total_users = UserRegistration.objects.count()
        total_applications = JobApplication.objects.count()
        pending_tasks = JobApplication.objects.filter(status='Pending').count()
    except:
        total_jobs = 0
        total_users = 0
        total_applications = 0
        pending_tasks = 0

    context = {
        'current_user': request.session.get('user_name', 'Admin'),
        'total_jobs': total_jobs,
        'total_users': total_users,
        'total_applications': total_applications,
        'pending_tasks': pending_tasks,
    }
    return render(request, 'admindashboard.html', context)
