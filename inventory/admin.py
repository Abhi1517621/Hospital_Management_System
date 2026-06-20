from django.contrib import admin
from .models import Beds, LabTestCatalog, MedicineInventory, InventoryTransactions

@admin.register(Beds)
class BedsAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'type', 'current_cost_per_day')
    list_filter = ('type',)

@admin.register(LabTestCatalog)
class LabTestCatalogAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'department', 'current_cost')

@admin.register(MedicineInventory)
class MedicineInventoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'current_stock_quantity', 'current_unit_price')
    search_fields = ('name',)

@admin.register(InventoryTransactions)
class InventoryTransactionsAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'transaction_type', 'quantity_change', 'timestamp')
    list_filter = ('transaction_type',)