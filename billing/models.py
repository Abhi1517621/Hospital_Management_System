import uuid
from django.db import models
from users.models import CustomUser
from clinical.models import Appointments, LabReports, Admissions, PrescriptionItems

class Invoices(models.Model):
    STATUS_CHOICES = [('Draft', 'Draft'), ('Unpaid', 'Unpaid'), ('Paid', 'Paid')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(CustomUser, on_delete=models.PROTECT, limit_choices_to={'role': 'Patient'}, related_name='invoices')
    appointment = models.OneToOneField('clinical.Appointments', on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid')
    generated_at = models.DateTimeField(auto_now_add=True)

class ConsultationCharges(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE, related_name='consultation_charges')
    appointment = models.ForeignKey(Appointments, on_delete=models.PROTECT, related_name='billing_charges')
    # Captures the doctor's fee AT THE TIME of the appointment
    charged_fee = models.DecimalField(max_digits=10, decimal_places=2)

class LabCharges(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE, related_name='lab_charges')
    lab_report = models.ForeignKey(LabReports, on_delete=models.PROTECT)
    charged_fee = models.DecimalField(max_digits=10, decimal_places=2)

class RoomCharges(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE, related_name='room_charges')
    admission = models.ForeignKey(Admissions, on_delete=models.PROTECT)
    days_billed = models.IntegerField()
    charged_daily_rate = models.DecimalField(max_digits=10, decimal_places=2)

class PharmacyCharges(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE, related_name='pharmacy_charges')
    prescription_item = models.ForeignKey(PrescriptionItems, on_delete=models.PROTECT)
    # Captures the medicine's price AT THE TIME it was dispensed
    charged_unit_price = models.DecimalField(max_digits=10, decimal_places=2)