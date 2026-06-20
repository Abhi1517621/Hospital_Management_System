from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction # The magic concurrency module
from .models import MedicineInventory, InventoryTransactions
from clinical.models import PrescriptionItems
from billing.utils import generate_visit_invoice
from billing.models import PharmacyCharges

@login_required(login_url='auth_gateway')
def pharmacist_dashboard(request):
    """Displays all prescriptions that haven't been dispensed yet."""
    if request.user.role != 'Pharmacist':
        return render(request, '403.html')

    # Fetch prescriptions where quantity_dispensed is 0
    pending_prescriptions = PrescriptionItems.objects.filter(quantity_dispensed=0).select_related('medical_record__patient', 'medicine')
    inventory = MedicineInventory.objects.all().order_by('name')

    context = {
        'pending_prescriptions': pending_prescriptions,
        'inventory': inventory
    }
    return render(request, 'inventory/pharmacist_dashboard.html', context)


@login_required(login_url='auth_gateway')
def dispense_medicine(request, prescription_id):
    if request.user.role != 'Pharmacist':
        return render(request, '403.html')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                prescription = get_object_or_404(PrescriptionItems, id=prescription_id)
                # Select for update to lock the row during concurrent dispensing
                medicine = MedicineInventory.objects.select_for_update().get(id=prescription.medicine.id)

                # SECURE OVERRIDE: Ignore any input. Dispense exactly what the doctor ordered.
                required_qty = prescription.quantity_prescribed

                if medicine.current_stock_quantity < required_qty:
                    messages.error(request, f"Insufficient stock. Need {required_qty}, but only have {medicine.current_stock_quantity}.")
                    return redirect('pharmacist_dashboard')

                # Deduct Inventory
                medicine.current_stock_quantity -= required_qty
                medicine.save()

                # Log Transaction
                InventoryTransactions.objects.create(
                    medicine=medicine, 
                    transaction_type='Dispense', 
                    quantity_change=-required_qty
                )

                # Mark as Fulfilled
                prescription.quantity_dispensed = required_qty
                prescription.save()

                # --- STRICT BILLING ROUTING ---
                # Fetch the exact invoice linked to this specific appointment
                invoice = prescription.medical_record.appointment.invoice
                
                item_total = float(medicine.current_unit_price) * required_qty
                
                PharmacyCharges.objects.create(
                    invoice=invoice,
                    prescription_item=prescription,
                    charged_unit_price=medicine.current_unit_price
                )
                
                invoice.total_amount = float(invoice.total_amount) + item_total
                invoice.save()

            messages.success(request, f"Successfully dispensed exactly {required_qty} units of {medicine.name}.")

        except Exception as e:
            messages.error(request, "Database error during transaction.")

    return redirect('pharmacist_dashboard')