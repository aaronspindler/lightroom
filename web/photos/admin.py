from django.contrib import admin

from .models import Photo

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('uploaded_by', 'created_at', 'updated_at')
    list_filter = ('uploaded_by', 'created_at', 'updated_at')
    search_fields = ('uploaded_by',)
    ordering = ('uploaded_by',)
    readonly_fields = ('image_tag',)