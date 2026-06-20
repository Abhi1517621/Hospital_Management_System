from django.contrib import admin
from .models import CustomUser, StaffProfile, PatientProfile, StaffLicenses

# Register the core models exactly ONCE
admin.site.register(CustomUser)
admin.site.register(StaffProfile)
admin.site.register(PatientProfile)

# Register the licenses with a custom view
@admin.register(StaffLicenses)
class StaffLicensesAdmin(admin.ModelAdmin):
    list_display = ('staff', 'license_type', 'license_number', 'expiry_date')
    search_fields = ('license_number',)