from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload_document_view, name='upload'),
    path('list/', views.document_list_view, name='list'),
    path('detail/<int:pk>/', views.document_detail_view, name='detail'),
    path('download/<int:pk>/', views.document_download_view, name='download'),
    path('delete/<int:pk>/', views.document_delete_view, name='delete'),
]