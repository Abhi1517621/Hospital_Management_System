from django.urls import path
from . import views

urlpatterns = [
    path('patient/pay/<uuid:invoice_id>/', views.pay_invoice, name='pay_invoice'),
    path('patient/invoice/<uuid:invoice_id>/', views.invoice_details, name='invoice_details'),
    ]
