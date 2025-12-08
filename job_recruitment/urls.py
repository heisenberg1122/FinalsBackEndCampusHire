from django.contrib import admin
from django.urls import path, include
from job_recruitmentapp import views as app_views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', app_views.admin_dashboard_view, name='admin_dashboard'),
    
    # API Routes
    path('api/login/', app_views.api_login),
    path('api/stats/', app_views.api_dashboard_stats),
    path('api/jobs/', app_views.api_jobs),
    path('api/jobs/<int:pk>/', app_views.api_job_detail), # <--- NEW for Edit/Delete
    # APP CONNECTIONS (Note the prefixes!)
    path('reg/', include('registration.urls')), 
    path('job/', include('job_recruitmentapp.urls')),
    path('user/', include('userapp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)