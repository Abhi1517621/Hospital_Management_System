from django.contrib import admin
from .models import Appointments, MedicalRecords, PrescriptionItems, LabReports, Admissions

@admin.register(Appointments)
class AppointmentsAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'scheduled_time', 'status')
    list_filter = ('status', 'scheduled_time')
    search_fields = ('patient__email', 'doctor__email')

@admin.register(MedicalRecords)
class MedicalRecordsAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'created_at')
    search_fields = ('patient__email', 'diagnosis')

@admin.register(PrescriptionItems)
class PrescriptionItemsAdmin(admin.ModelAdmin):
    list_display = ('medical_record', 'medicine', 'quantity_dispensed')

@admin.register(LabReports)
class LabReportsAdmin(admin.ModelAdmin):
    list_display = ('patient', 'lab_test', 'status', 'generated_at')
    list_filter = ('status',)

@admin.register(Admissions)
class AdmissionsAdmin(admin.ModelAdmin):
    list_display = ('patient', 'bed', 'attending_doctor', 'admitted_at', 'discharged_at')
    list_filter = ('admitted_at', ('discharged_at', admin.EmptyFieldListFilter))