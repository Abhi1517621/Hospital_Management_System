from django.urls import path
from . import views

urlpatterns = [
    path('pharmacist/dashboard/', views.pharmacist_dashboard, name='pharmacist_dashboard'),
    path('pharmacist/dispense/<uuid:prescription_id>/', views.dispense_medicine, name='dispense_medicine'),
]