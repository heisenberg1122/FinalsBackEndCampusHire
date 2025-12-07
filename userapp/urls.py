from django.urls import path
from . import views

app_name = 'userapp'

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('apply/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.user_profile_edit, name='user_profile_edit'),
]