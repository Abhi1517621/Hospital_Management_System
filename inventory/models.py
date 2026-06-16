import uuid
from django.db import models

class MedicineInventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=200)
    current_stock_quantity = models.IntegerField(default=0)
    current_unit_price = models.DecimalField(max_digits=10, decimal_places=2)

class InventoryTransactions(models.Model):
    TXN_CHOICES = [('Restock', 'Restock'), ('Dispense', 'Dispense'), ('Adjustment', 'Adjustment')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medicine = models.ForeignKey(MedicineInventory, on_delete=models.PROTECT, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TXN_CHOICES)
    quantity_change = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

class LabTestCatalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    current_cost = models.DecimalField(max_digits=10, decimal_places=2)

class Beds(models.Model):
    BED_CHOICES = [('ICU', 'ICU'), ('General', 'General'), ('Pediatric', 'Pediatric')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_number = models.CharField(max_length=20)
    type = models.CharField(max_length=50, choices=BED_CHOICES)
    current_cost_per_day = models.DecimalField(max_digits=10, decimal_places=2)