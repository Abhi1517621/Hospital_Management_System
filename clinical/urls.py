from django.urls import path
from . import views

urlpatterns = [
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/consult/<uuid:appointment_id>/', views.consultation_view, name='consultation'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/update-profile/', views.update_patient_profile, name='update_patient_profile'),
    path('patient/book-appointment/', views.book_appointment, name='book_appointment'),
    path('lab/dashboard/', views.lab_dashboard, name='lab_dashboard'),
    path('lab/process/<uuid:report_id>/', views.process_lab_test, name='process_lab_test'),
    path('doctor/discharge/<uuid:admission_id>/', views.discharge_patient, name='discharge_patient'),
]