from django.contrib import admin
from .models import Invoices, ConsultationCharges, LabCharges, RoomCharges, PharmacyCharges

@admin.register(Invoices)
class InvoicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'total_amount', 'status', 'generated_at')
    list_filter = ('status',)
    search_fields = ('patient__email',)

# Registering the line items for complete transparency
admin.site.register(ConsultationCharges)
admin.site.register(LabCharges)
admin.site.register(RoomCharges)
admin.site.register(PharmacyCharges)