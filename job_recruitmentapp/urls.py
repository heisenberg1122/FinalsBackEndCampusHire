from django.urls import path
from . import views

app_name = "jobs" 

urlpatterns = [
    # API Routes
    path('api/jobs/', views.api_jobs), 
    path('api/jobs/<int:pk>/', views.api_job_detail), # <--- NEW for Edit/Delete
    path('api/applications/', views.api_applications, name='api_applications'), 
    path('api/apply/', views.api_apply_job, name='api_apply_job'),
    path('api/application_history/<int:user_id>/', views.application_history, name='application_history'),
    path('api/applications/<int:pk>/', views.delete_application, name='delete_application'),
    # In urlpatterns:
    path('api/applications/<int:pk>/status/', views.api_update_application_status),
    path('api/interviews/', views.api_interview_list, name='api_interviews'),
    # Use a CSRF-exempt plain Django view for mobile POSTs to avoid DRF/CSRF conflicts
    path('api/interviews/create/', views.interview_create_no_csrf, name='interview_create'),
    path('api/interviews/<int:pk>/delete/', views.delete_interview, name='delete_interview'),
# --- Notifications (NEW) ---
    path('api/notifications/<int:user_id>/', views.api_user_notifications, name='api_user_notifications'),
    path('api/notifications/create/', views.api_create_notification, name='api_create_notification'),
    path('api/notifications/<int:pk>/mark_read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/<int:pk>/delete/', views.api_delete_notification, name='api_delete_notification'),
    # Desktop HTML Routes
    path('list/', views.jobs_html, name='jobs_html'),
    path('add/', views.job_create_html, name='job_create_html'),
    path('<int:pk>/edit/', views.job_update_html, name='job_update_html'),
    path('<int:pk>/delete/', views.job_delete_html, name='job_delete_html'),
    path('applicants/', views.application_list, name='application_list'),
    path('tasks/', views.pending_tasks, name='pending_tasks'),
    path('settings/', views.system_settings, name='system_settings'),
    path('interviews/', views.interview_list, name='interview_list'),
    path('interviews/schedule/<int:application_id>/', views.interview_create, name='interview_create'),
    # API review endpoint (used by mobile / React Native)
    path('review/<int:pk>/', views.api_review_application, name='review_application'),
]