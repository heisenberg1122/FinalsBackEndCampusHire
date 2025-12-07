from django.urls import path
from . import views

app_name = "jobs" 

urlpatterns = [
    # API Routes
    path('api/jobs/', views.api_jobs), 
    path('api/jobs/<int:pk>/', views.api_job_detail), # <--- NEW for Edit/Delete
    path('api/applications/', views.api_applications, name='api_applications'), 
    path('api/apply/', views.api_apply_job, name='api_apply_job'),
    # In urlpatterns:
    path('api/applications/<int:pk>/status/', views.api_update_application_status),

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
    path('review/<int:pk>/', views.review_application, name='review_application'),
]