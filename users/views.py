from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser, StaffProfile, PatientProfile
from .models import StaffLicenses

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
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = request.POST.get('role')
            
            # Capture the new fields
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
            else:
                # Pass the names into the create_user method
                user = CustomUser.objects.create_user(
                    email=email, 
                    password=password, 
                    role=role,
                    first_name=first_name,
                    last_name=last_name
                )
                
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
    The Main Routing Hub. Checks the user's role and state before directing them.
    """
    user = request.user

    if user.role == 'Doctor':
        # Check if the doctor has completed their profile (specialization is not null)
        profile = getattr(user, 'staff_profile', None)
        if profile and not profile.specialization:
            return redirect('complete_profile')
        return redirect('doctor_dashboard') # We will build this next

    elif user.role == 'Patient':
        return redirect('patient_dashboard') # Placeholder for later
    
    elif user.role == 'Pharmacist':
        return redirect('pharmacist_dashboard') # Add this routing rule
    elif user.role == 'LabTech':
        return redirect('lab_dashboard')

    # Fallback for other roles (Admin, Nurse, etc.)
    return render(request, 'dashboard.html')


@login_required(login_url='auth_gateway')
def complete_profile(request):
    """
    Forces Doctors/Staff to input their specialization, fee, and medical license.
    Matches the StaffProfile and StaffLicenses tables exactly.
    """
    user = request.user
    profile = getattr(user, 'staff_profile', None)

    # Security check: Only let staff with incomplete profiles access this
    if not profile or profile.specialization:
        return redirect('dashboard')

    if request.method == 'POST':
        # Update StaffProfile
        profile.specialization = request.POST.get('specialization')
        profile.base_consultation_fee = request.POST.get('base_consultation_fee')
        profile.save()

        # Insert into StaffLicenses
        StaffLicenses.objects.create(
            staff=profile,
            license_type=request.POST.get('license_type'),
            license_number=request.POST.get('license_number'),
            expiry_date=request.POST.get('expiry_date')
        )
        
        messages.success(request, "Profile completed successfully. Welcome to the portal.")
        return redirect('doctor_dashboard')

    return render(request, 'complete_profile.html')

def logout_view(request):
    """Securely terminates the user session."""
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('auth_gateway')

def home_page(request):
    """The master landing page for the entire hospital network."""
    return render(request, 'index.html')