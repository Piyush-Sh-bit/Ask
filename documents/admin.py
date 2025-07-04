from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'doc_type', 'uploaded_at')
    list_filter = ('doc_type', 'uploaded_at')
    search_fields = ('title', 'user__email', 'tags')
    readonly_fields = ('uploaded_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)