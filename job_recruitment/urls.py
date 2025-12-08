from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter  # <--- 1. Import DefaultRouter

# --- IMPORT VIEWS ---
from job_recruitmentapp import views as app_views
from userapp.views import UserViewSet  # <--- 2. Import UserViewSet (Make sure this exists in userapp/views.py)

# --- REGISTER ROUTER ---
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user') # <--- 3. This creates the /api/users/ endpoint

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', app_views.admin_dashboard_view, name='admin_dashboard'),
    
    # --- API ROUTES ---
    # This line connects the router. Now /api/users/ will exist!
    path('api/', include(router.urls)), 

    # Your existing manual API routes (Keep these)
    path('api/login/', app_views.api_login),
    path('api/stats/', app_views.api_dashboard_stats),
    path('api/jobs/', app_views.api_jobs),
    path('api/jobs/<int:pk>/', app_views.api_job_detail),

    # --- APP CONNECTIONS ---
    path('reg/', include('registration.urls')), 
    path('job/', include('job_recruitmentapp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)