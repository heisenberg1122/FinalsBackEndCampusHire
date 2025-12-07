from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserRegistration
from .serializer import RegistrationSerializer, UserSerializer

# ===========================
#  API VIEWS (Mobile App)
# ===========================

@api_view(['POST'])
def register_user(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_users(request):
    # This fixes "Failed to fetch users" on mobile
    users = UserRegistration.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET', 'DELETE'])
def user_detail(request, pk):
    try:
        user = UserRegistration.objects.get(pk=pk)
    except UserRegistration.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===========================
#  HTML VIEWS (Desktop Web)
# ===========================

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = UserRegistration.objects.get(email=email)
            if user.password == password: # Use check_password in production
                request.session['user_id'] = user.id
                request.session['user_name'] = f"{user.first_name} {user.last_name}"
                request.session['role'] = user.role
                
                if user.role == 'Admin':
                    return redirect('admin_dashboard') # Goes to HR Dashboard
                else:
                    return redirect('userapp:user_dashboard')
            else:
                messages.error(request, "Invalid password")
        except UserRegistration.DoesNotExist:
            messages.error(request, "User not found")
    return render(request, 'registration/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('registration:login_view')

def public_register_view(request):
    # ... (Keep your existing register logic if needed) ...
    return render(request, 'registration/register.html')

# --- Admin User Management (HTML) ---
def users_html(request):
    users = UserRegistration.objects.all()
    return render(request, 'registration/users_list.html', {'users': users})

def user_create_html(request):
    # ... logic to create user ...
    return render(request, 'registration/user_form.html')

def user_update_html(request, pk):
    # ... logic to update user ...
    return render(request, 'registration/user_form.html')

def user_delete_html(request, pk):
    # ... logic to delete user ...
    return render(request, 'registration/user_confirm_delete.html')

def admin_profile(request):
    return render(request, 'registration/admin_profile.html')

def admin_profile_edit(request):
    return render(request, 'registration/admin_profile_edit.html')