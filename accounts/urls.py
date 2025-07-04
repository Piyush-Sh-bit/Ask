from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='accounts:register'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Role-based dashboards
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    
    # Doctor views for patients
    path('patients/', views.patient_list_view, name='patient_list'),
    path('patients/<int:patient_id>/', views.patient_detail_view, name='patient_detail'),
    path('patients/<int:patient_id>/documents/<int:document_id>/', views.patient_document_view, name='patient_document'),
]