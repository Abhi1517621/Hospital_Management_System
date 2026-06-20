import uuid
from django.db import models
from users.models import CustomUser
from inventory.models import MedicineInventory, LabTestCatalog, Beds

class Appointments(models.Model):
    STATUS_CHOICES = [('Scheduled', 'Scheduled'), ('In-Progress', 'In-Progress'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Patient'}, related_name='appointments_as_patient')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Doctor'}, related_name='appointments_as_doctor')
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    notes = models.TextField(blank=True, null=True)

class MedicalRecords(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.OneToOneField(Appointments, on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_record')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Patient'}, related_name='medical_records_as_patient')
    doctor = models.ForeignKey(CustomUser, on_delete=models.PROTECT, limit_choices_to={'role': 'Doctor'}, related_name='medical_records_as_doctor')
    diagnosis = models.TextField()
    prescription_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PrescriptionItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medical_record = models.ForeignKey(MedicalRecords, on_delete=models.CASCADE, related_name='prescribed_items')
    medicine = models.ForeignKey(MedicineInventory, on_delete=models.PROTECT, related_name='prescriptions')
    dosage = models.CharField(max_length=100)
    quantity_prescribed = models.IntegerField(default=1) 
    quantity_dispensed = models.IntegerField(default=0)
class LabReports(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Completed', 'Completed')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Patient'}, related_name='lab_reports_as_patient')
    lab_test = models.ForeignKey(LabTestCatalog, on_delete=models.PROTECT, related_name='reports')
    technician = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'LabTech'}, related_name='lab_reports_as_technician')
    result_data = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    generated_at = models.DateTimeField(auto_now_add=True)
    appointment = models.ForeignKey(Appointments, on_delete=models.CASCADE, related_name='lab_reports', null=True, blank=True)
class Admissions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Patient'}, related_name='admissions_as_patient')
    bed = models.ForeignKey(Beds, on_delete=models.PROTECT, related_name='admissions')
    attending_doctor = models.ForeignKey(CustomUser, on_delete=models.PROTECT, limit_choices_to={'role': 'Doctor'}, related_name='admissions_as_doctor')
    admitted_at = models.DateTimeField(auto_now_add=True)
    discharged_at = models.DateTimeField(null=True, blank=True)
    appointment = models.ForeignKey(Appointments, on_delete=models.CASCADE, related_name='admissions', null=True, blank=True)