from django.contrib import admin
from .models import CustomUser, StaffProfile

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'id', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'deleted_at')

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'clearance_level')
    search_fields = ('user__email', 'specialization')