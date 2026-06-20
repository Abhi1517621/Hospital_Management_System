from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Invoices
from django.shortcuts import render, redirect, get_object_or_404 


@login_required(login_url='auth_gateway')
def pay_invoice(request, invoice_id):
    """
    A mock payment gateway route. Safely verifies the invoice belongs 
    to the logged-in patient before flipping the status.
    """
    if request.user.role != 'Patient':
        return render(request, '403.html')

    if request.method == 'POST':
        # Security: Ensure patients can only pay THEIR OWN invoices
        invoice = get_object_or_404(Invoices, id=invoice_id, patient=request.user)

        if invoice.status == 'Unpaid':
            # Mocking the successful payment transaction
            invoice.status = 'Paid'
            invoice.save()
            messages.success(request, f"Payment of ₹{invoice.total_amount} processed successfully!")
        else:
            messages.info(request, "This invoice has already been settled.")

    # Redirect back to the dashboard regardless of outcome
    return redirect('patient_dashboard')

@login_required(login_url='auth_gateway')
def invoice_details(request, invoice_id):
    """Generates an itemized receipt for the patient."""
    if request.user.role != 'Patient':
        return render(request, '403.html')

    # Security: Ensure they can only view their own invoice
    invoice = get_object_or_404(Invoices, id=invoice_id, patient=request.user)

    # Gather all related historical line items
    context = {
        'invoice': invoice,
        'consultation': invoice.consultation_charges.first(),
        'pharmacy_items': invoice.pharmacy_charges.all(),
        'lab_items': invoice.lab_charges.all(),
        'room_items': invoice.room_charges.first()
    }
    
    return render(request, 'billing/invoice_details.html', context)