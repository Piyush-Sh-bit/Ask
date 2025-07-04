from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser
from .decorators import doctor_required, patient_required
from documents.models import Document

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            messages.success(request, f'Account created for {email}!')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                # Role-based redirection
                if user.role == 'doctor':
                    return redirect('accounts:doctor_dashboard')
                else:  # patient
                    return redirect('accounts:patient_dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@patient_required
def patient_dashboard(request):
    """Dashboard for patients - shows their own documents"""
    documents = Document.objects.filter(user=request.user)[:5]
    total_documents = Document.objects.filter(user=request.user).count()
    
    context = {
        'documents': documents,
        'total_documents': total_documents,
        'user': request.user,
        'dashboard_type': 'patient'
    }
    return render(request, 'accounts/patient_dashboard.html', context)

@doctor_required
def doctor_dashboard(request):
    """Dashboard for doctors - shows overview of all patients"""
    patients = CustomUser.objects.filter(role='patient')
    total_patients = patients.count()
    total_documents = Document.objects.count()
    recent_documents = Document.objects.all()[:5]
    
    context = {
        'patients': patients,
        'total_patients': total_patients,
        'total_documents': total_documents,
        'recent_documents': recent_documents,
        'user': request.user,
        'dashboard_type': 'doctor'
    }
    return render(request, 'accounts/doctor_dashboard.html', context)

@doctor_required
def patient_list_view(request):
    """View for doctors to see all patients"""
    search_query = request.GET.get('search', '')
    patients = CustomUser.objects.filter(role='patient')
    
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'patients': patients,
        'search_query': search_query,
    }
    return render(request, 'accounts/patient_list.html', context)

@doctor_required
def patient_detail_view(request, patient_id):
    """View for doctors to see patient details and documents"""
    patient = get_object_or_404(CustomUser, id=patient_id, role='patient')
    documents = Document.objects.filter(user=patient)
    
    # Filter documents by type if requested
    doc_type = request.GET.get('doc_type')
    if doc_type:
        documents = documents.filter(doc_type=doc_type)
    
    context = {
        'patient': patient,
        'documents': documents,
        'total_documents': documents.count(),
        'doc_type_filter': doc_type,
        'document_types': Document.DOCUMENT_TYPES,
    }
    return render(request, 'accounts/patient_detail.html', context)

@doctor_required
def patient_document_view(request, patient_id, document_id):
    """View for doctors to see specific patient document"""
    patient = get_object_or_404(CustomUser, id=patient_id, role='patient')
    document = get_object_or_404(Document, id=document_id, user=patient)
    
    context = {
        'patient': patient,
        'document': document,
    }
    return render(request, 'accounts/patient_document.html', context)