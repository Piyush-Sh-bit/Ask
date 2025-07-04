from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.db.models import Q
from .models import Document
from .forms import DocumentUploadForm, DocumentSearchForm
from accounts.decorators import patient_required
import os

@login_required
def dashboard_view(request):
    # Redirect based on user role
    if request.user.role == 'doctor':
        return redirect('accounts:doctor_dashboard')
    else:
        return redirect('accounts:patient_dashboard')

@patient_required
def upload_document_view(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('documents:list')
    else:
        form = DocumentUploadForm()
    return render(request, 'documents/upload.html', {'form': form})

@patient_required
def document_list_view(request):
    documents = Document.objects.filter(user=request.user)
    search_form = DocumentSearchForm(request.GET)
    
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        doc_type = search_form.cleaned_data.get('doc_type')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if search_query:
            documents = documents.filter(
                Q(title__icontains=search_query) |
                Q(tags__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if doc_type:
            documents = documents.filter(doc_type=doc_type)
        
        if date_from:
            documents = documents.filter(uploaded_at__date__gte=date_from)
        
        if date_to:
            documents = documents.filter(uploaded_at__date__lte=date_to)
    
    context = {
        'documents': documents,
        'search_form': search_form,
    }
    return render(request, 'documents/list.html', context)

@login_required
def document_detail_view(request, pk):
    # Patients can only see their own documents
    # Doctors can see any document (for patient care)
    if request.user.role == 'patient':
        document = get_object_or_404(Document, pk=pk, user=request.user)
    else:  # doctor
        document = get_object_or_404(Document, pk=pk)
    
    return render(request, 'documents/detail.html', {'document': document})

@login_required
def document_download_view(request, pk):
    # Patients can only download their own documents
    # Doctors can download any document (for patient care)
    if request.user.role == 'patient':
        document = get_object_or_404(Document, pk=pk, user=request.user)
    else:  # doctor
        document = get_object_or_404(Document, pk=pk)
    
    if os.path.exists(document.file.path):
        with open(document.file.path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(document.file.name)}"'
            return response
    raise Http404

@patient_required
def document_delete_view(request, pk):
    document = get_object_or_404(Document, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Delete the file from filesystem
        if os.path.exists(document.file.path):
            os.remove(document.file.path)
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('documents:list')
    
    return render(request, 'documents/delete_confirm.html', {'document': document})