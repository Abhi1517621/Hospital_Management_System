from django.db import transaction
from .models import Invoices, ConsultationCharges, PharmacyCharges

from django.db import transaction
from .models import Invoices, ConsultationCharges

@transaction.atomic
def generate_visit_invoice(appointment):
    """
    Creates the master invoice mapped strictly to a single appointment.
    Applies the base consultation fee. Other departments will append to this invoice.
    """
    # Create the invoice linked strictly to this appointment
    invoice, created = Invoices.objects.get_or_create(
        appointment=appointment,
        defaults={
            'patient': appointment.patient,
            'status': 'Unpaid',
            'total_amount': 0.00
        }
    )
    
    # Only add the doctor's fee if the invoice was just created
    if created:
        fee = appointment.doctor.staff_profile.base_consultation_fee
        ConsultationCharges.objects.create(
            invoice=invoice,
            appointment=appointment,
            charged_fee=fee
        )
        invoice.total_amount = fee
        invoice.save()
        
    return invoice