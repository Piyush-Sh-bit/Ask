from django.db import models
from django.conf import settings
import os

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.id}/{filename}'

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('prescription', 'Prescription'),
        ('report', 'Medical Report'),
        ('scan', 'Medical Scan'),
        ('lab_result', 'Lab Result'),
        ('insurance', 'Insurance Document'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=user_directory_path)
    doc_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='other')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()
    
    def is_pdf(self):
        return self.get_file_extension() == '.pdf'
    
    def is_image(self):
        return self.get_file_extension() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']