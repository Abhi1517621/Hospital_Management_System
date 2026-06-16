from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser, StaffProfile, PatientProfile

def auth_gateway(request):
    """
    Handles both Login and Sign-Up POST requests, and serves the HTML gateway.
    """
    # If user is already logged in, redirect them to their respective dashboard
    if request.user.is_authenticated:
        return redirect('dashboard') # We will create this route later

    if request.method == 'POST':
        action = request.POST.get('action')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # --- LOGIN LOGIC ---
        if action == 'login':
            # authenticate() checks the hashed password in the DB safely
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user) # Establishes the secure session cookie
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid email or password.")

        # --- SIGNUP LOGIC ---
        elif action == 'signup':
            role = request.POST.get('role')
            
            # Basic validation
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
            else:
                # Use our CustomUserManager to safely hash the password and create the user
                user = CustomUser.objects.create_user(email=email, password=password, role=role)
                
                # If it's a staff role, create the linked StaffProfile (1-to-1 UUID relation)
                if role in ['Doctor', 'Nurse', 'Pharmacist', 'LabTech']:
                    StaffProfile.objects.create(user=user)
                elif role == 'Patient':
                    PatientProfile.objects.create(user=user)

                messages.success(request, "Account created successfully. Please log in.")
                return redirect('auth_gateway')

    return render(request, 'auth.html')

def logout_view(request):
    logout(request)
    return redirect('auth_gateway')

@login_required(login_url='auth_gateway')
def dashboard_view(request):
    """
    The main routing hub after a successful login.
    Later, we will add logic here to redirect Doctors to a doctor view, 
    Patients to a patient view, etc., based on request.user.role.
    """
    return render(request, 'dashboard.html')