from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.auth_gateway, name='auth_gateway'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]