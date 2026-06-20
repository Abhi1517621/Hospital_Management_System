from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required
from .models import Appointments, MedicalRecords 
from django.utils import timezone
import datetime
from datetime import timedelta
from django.contrib import messages
from inventory.models import MedicineInventory
from clinical.models import PrescriptionItems
from users.models import CustomUser
from inventory.models import LabTestCatalog
from clinical.models import LabReports
from billing.models import Invoices, LabCharges
from django.db import transaction
from inventory.models import Beds
from clinical.models import Admissions
from billing.models import RoomCharges
from billing.utils import generate_visit_invoice

@login_required(login_url='auth_gateway')
def doctor_dashboard(request):
    """Master dashboard for Doctors combining scheduling and admissions."""
    if request.user.role != 'Doctor':
        return render(request, '403.html')

    # Time boundaries for safe querying
    now = timezone.now()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_tomorrow = start_of_today + datetime.timedelta(days=1)

    # 1. Fetch Today's Queue
    appointments = Appointments.objects.filter(
        doctor=request.user, 
        scheduled_time__gte=start_of_today,
        scheduled_time__lt=start_of_tomorrow
    ).order_by('scheduled_time')

    # 2. Fetch Future Queue
    upcoming_appointments = Appointments.objects.filter(
        doctor=request.user,
        scheduled_time__gte=start_of_tomorrow
    ).order_by('scheduled_time')

    # 3. Fetch Active Admissions (Using select_related for efficiency)
    active_admissions = Admissions.objects.filter(
        attending_doctor=request.user, 
        discharged_at__isnull=True
    ).select_related('patient', 'bed')

    # 4. Assemble the context right before the return statement
    context = {
        'doctor_profile': request.user.staff_profile,
        'appointments': appointments,
        'upcoming_appointments': upcoming_appointments,
        'active_admissions': active_admissions,
        'today': now.date()
    }
    
    return render(request, 'clinical/doctor_dashboard.html', context)

@login_required(login_url='auth_gateway')
def consultation_view(request, appointment_id):
    if request.user.role != 'Doctor':
        return render(request, '403.html')

    appointment = get_object_or_404(Appointments, id=appointment_id, doctor=request.user)
    # NEW SECURITY LOCK:
    if appointment.status == 'Completed':
        messages.error(request, "This consultation has already been completed and locked.")
        return redirect('doctor_dashboard')
    medicines = MedicineInventory.objects.all().order_by('name')
    lab_tests = LabTestCatalog.objects.all().order_by('test_name')
    
    # Calculate available beds dynamically
    occupied_beds = Admissions.objects.filter(discharged_at__isnull=True).values_list('bed_id', flat=True)
    available_beds = Beds.objects.exclude(id__in=occupied_beds)

    if request.method == 'POST':
        diagnosis = request.POST.get('diagnosis')
        notes = request.POST.get('prescription_notes')
        
        medicine_id = request.POST.get('medicine_id')
        dosage = request.POST.get('dosage')
        quantity = request.POST.get('quantity')
        lab_test_id = request.POST.get('lab_test_id')
        
        # NEW: Catch the bed assignment
        bed_id = request.POST.get('bed_id')

        # 1. Medical Record
        record = MedicalRecords.objects.create(
            appointment=appointment, patient=appointment.patient,
            doctor=request.user, diagnosis=diagnosis, prescription_notes=notes
        )

        # 2. Prescribe Medicine (Secure Implementation)
        if medicine_id and quantity:
            selected_medicine = get_object_or_404(MedicineInventory, id=medicine_id)
            PrescriptionItems.objects.create(
                medical_record=record, 
                medicine=selected_medicine,
                dosage=dosage, # Keep this clean now! (e.g. "2x Daily")
                quantity_prescribed=int(quantity), # Lock the exact amount
                quantity_dispensed=0
            )
            
        # 3. Labs
        if lab_test_id:
            selected_test = get_object_or_404(LabTestCatalog, id=lab_test_id)
            LabReports.objects.create(
                patient=appointment.patient, 
                lab_test=selected_test,
                appointment=appointment # NEW
            )

        # 4. Hospital Admission
        if bed_id:
            selected_bed = get_object_or_404(Beds, id=bed_id)
            Admissions.objects.create(
                patient=appointment.patient,
                bed=selected_bed,
                attending_doctor=request.user,
                appointment=appointment # NEW
            )

        # 5. Complete Appointment & Generate Initial Invoice
        appointment.status = 'Completed'
        appointment.save()
        # NEW: Create the invoice immediately!        
        generate_visit_invoice(appointment)
        messages.success(request, "Consultation completed. All orders and admissions processed.")
        return redirect('doctor_dashboard')

    return render(request, 'clinical/consultation.html', {
        'appointment': appointment, 
        'medicines': medicines,
        'lab_tests': lab_tests,
        'available_beds': available_beds # Pass to template
    })

@login_required(login_url='auth_gateway')
def patient_dashboard(request):
    """
    The main operational view for a Patient.
    Simply lists their profile UUID and their upcoming/past appointments.
    """
    if request.user.role != 'Patient':
        return render(request, '403.html')

    appointments = Appointments.objects.filter(patient=request.user).order_by('scheduled_time')
    
    # Fetch all invoices for this patient
    invoices = Invoices.objects.filter(patient=request.user).order_by('-generated_at')
    lab_reports = LabReports.objects.filter(patient=request.user).order_by('-generated_at')
    admissions = Admissions.objects.filter(patient=request.user).order_by('-admitted_at')
    context = {
        'patient_profile': request.user.patient_profile,
        'appointments': appointments,
        'invoices': Invoices.objects.filter(patient=request.user).order_by('-generated_at'),
        'lab_reports': lab_reports,   # NEW
        'admissions': admissions,     # NEW
    }
    return render(request, 'clinical/patient_dashboard.html', context)

@login_required(login_url='auth_gateway')
def update_patient_profile(request):
    """Allows patients to update their emergency and medical details."""
    if request.user.role != 'Patient':
        return render(request, '403.html')

    profile = request.user.patient_profile

    if request.method == 'POST':
        profile.blood_group = request.POST.get('blood_group')
        profile.emergency_contact = request.POST.get('emergency_contact')
        profile.save()
        
        return redirect('patient_dashboard')

    return render(request, 'clinical/update_profile.html', {'profile': profile})

@login_required(login_url='auth_gateway')
def book_appointment(request):
    if request.user.role != 'Patient':
        return render(request, '403.html')

    # 1. Calculate the exact 3-day rolling window
    today = timezone.now().date()
    max_allowed_date = today + timedelta(days=3)

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        scheduled_datetime_str = request.POST.get('scheduled_time') 
        notes = request.POST.get('notes', '')

        try:
            # 1. Parse the string and make it strictly Timezone Aware!
            naive_time = datetime.datetime.fromisoformat(scheduled_datetime_str)
            scheduled_time = timezone.make_aware(naive_time) 
            scheduled_date = scheduled_time.date()
        except ValueError:
            messages.error(request, "Invalid date format submitted.")
            return redirect('book_appointment')

        # --- UPDATED BACKEND SECURITY ---
        now = timezone.now()

        # Check 1: Is the exact time in the past? (Catches 14:30 if it's currently 14:50)
        if scheduled_time < now:
            messages.error(request, "Security Error: Cannot book an appointment for a time that has already passed.")
            return redirect('book_appointment')
            
        # Check 2: Is it beyond the 3-day window?
        if scheduled_date > max_allowed_date:
            messages.error(request, "Security Error: Appointments can only be booked up to 3 days in advance.")
            return redirect('book_appointment')
        # --------------------------------

        # 3. Create the Appointment
        selected_doctor = get_object_or_404(CustomUser, id=doctor_id, role='Doctor')
        Appointments.objects.create(
            patient=request.user,
            doctor=selected_doctor,
            scheduled_time=scheduled_time,
            notes=notes
        )
        
        messages.success(request, f"Appointment confirmed with Dr. {selected_doctor.last_name} for {scheduled_time.strftime('%b %d, %Y at %H:%M')}.")
        return redirect('patient_dashboard')

    # Fetch active doctors for the dropdown
    doctors = CustomUser.objects.filter(role='Doctor', is_active=True).select_related('staff_profile')

    # Pass the calculated boundaries to the template
    # HTML5 datetime-local requires a specific string format (YYYY-MM-DDTHH:MM)
    context = {
        'doctors': doctors,
        'min_datetime': timezone.now().strftime('%Y-%m-%dT%H:%M'), 
        'max_datetime': (timezone.now() + timedelta(days=3)).replace(hour=23, minute=59).strftime('%Y-%m-%dT%H:%M')
    }
    
    return render(request, 'clinical/book_appointment.html', context)

@login_required(login_url='auth_gateway')
def lab_dashboard(request):
    if request.user.role != 'LabTech':
        return render(request, '403.html')

    # Fetch all pending tests across the hospital
    pending_tests = LabReports.objects.filter(status='Pending').order_by('-generated_at')
    return render(request, 'clinical/lab_dashboard.html', {'pending_tests': pending_tests})


@login_required(login_url='auth_gateway')
def process_lab_test(request, report_id):
    if request.user.role != 'LabTech':
        return render(request, '403.html')

    report = get_object_or_404(LabReports, id=report_id)

    if request.method == 'POST':
        result_data = request.POST.get('result_data')

        try:
            with transaction.atomic():
                # 1. Update the Clinical Record
                report.result_data = result_data
                report.technician = request.user
                report.status = 'Completed'
                report.save()

                # 2. Strict Financial Ledger Integration
                invoice = report.appointment.invoice
                test_cost = report.lab_test.current_cost
                
                LabCharges.objects.create(
                    invoice=invoice,
                    lab_report=report,
                    charged_fee=test_cost
                )
                
                invoice.total_amount = float(invoice.total_amount) + float(test_cost)
                invoice.save()

            messages.success(request, f"Results submitted and billed for {report.lab_test.test_name}.")
            return redirect('lab_dashboard')
            
        except Exception as e:
            messages.error(request, "Error processing lab results.")

    return render(request, 'clinical/process_lab.html', {'report': report})

@login_required(login_url='auth_gateway')
@transaction.atomic
def discharge_patient(request, admission_id):
    if request.user.role != 'Doctor':
        return render(request, '403.html')

    admission = get_object_or_404(Admissions, id=admission_id)
    
    # SECURITY LOCK: Prevent double-discharge
    if admission.discharged_at is not None:
        messages.error(request, "Patient is already discharged.")
        return redirect('doctor_dashboard')

    if request.method == 'POST':
        # 1. Record the discharge time
        admission.discharged_at = timezone.now()
        admission.save()

        # 2. Calculate billable days
        duration = admission.discharged_at - admission.admitted_at
        days = max(1, duration.days)  # Minimum 1 day billed

        # 3. Strict Financial Ledger Integration
        invoice = admission.appointment.invoice

        room_rate = admission.bed.current_cost_per_day
        total_room_cost = float(room_rate) * days

        RoomCharges.objects.create(
            invoice=invoice,
            admission=admission,
            days_billed=days,
            charged_daily_rate=room_rate
        )

        invoice.total_amount = float(invoice.total_amount) + total_room_cost
        invoice.save()

        messages.success(request, f"Patient discharged safely. Billed for {days} day(s).")
        
    return redirect('doctor_dashboard')