from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from .models import Faces
from .tasks import generate_face_encoding_async
from .views import FaceEncodingCache
import logging

logger = logging.getLogger(__name__)


class FacesAdmin(admin.ModelAdmin):
    list_display = ('person_display', 'has_encoding', 'encoding_status', 'actions_display')
    list_filter = ('personId__firstName', 'personId__lastName')
    search_fields = ('personId__firstName', 'personId__lastName', 'personId__id')
    readonly_fields = ('encoding_info',)
    
    fieldsets = (
        ('Person Information', {
            'fields': ('personId',)
        }),
        ('Images', {
            'fields': ('pics', 'pics2', 'pics3'),
            'classes': ('collapse',)
        }),
        ('Face Encoding', {
            'fields': ('faceEncoding', 'encoding_info'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['generate_encoding', 'clear_cache_action']
    
    def person_display(self, obj):
        """Display person name"""
        return f"{obj.personId.firstName} {obj.personId.lastName}"
    person_display.short_description = 'Person'
    
    def has_encoding(self, obj):
        """Show if encoding exists"""
        if obj.faceEncoding:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Yes</span>'
            )
        return format_html(
            '<span style="color: red;">✗ No</span>'
        )
    has_encoding.short_description = 'Has Encoding'
    
    def encoding_status(self, obj):
        """Show encoding status"""
        if not obj.faceEncoding:
            return format_html(
                '<span style="color: orange;">Pending</span>'
            )
        # Get encoding size
        size_kb = len(obj.faceEncoding) / 1024
        return format_html(
            '<span style="color: green;">{:.1f} KB</span>',
            size_kb
        )
    encoding_status.short_description = 'Status'
    
    def encoding_info(self, obj):
        """Display encoding information"""
        if not obj.faceEncoding:
            return "No encoding generated"
        
        size = len(obj.faceEncoding)
        return f"Encoding size: {size} bytes ({size/1024:.1f} KB)"
    encoding_info.short_description = 'Encoding Information'
    
    def actions_display(self, obj):
        """Quick action buttons"""
        buttons = []
        
        if not obj.faceEncoding:
            buttons.append(format_html(
                '<a class="button" href="?action=generate_encoding&ids={}">Generate</a>',
                obj.id
            ))
        
        return format_html(' '.join(buttons))
    actions_display.short_description = 'Quick Actions'
    
    def generate_encoding(self, request, queryset):
        """Admin action to generate face encoding"""
        updated = 0
        failed = 0
        
        for face in queryset:
            if generate_face_encoding_async(face.id):
                updated += 1
            else:
                failed += 1
        
        # Clear cache
        FaceEncodingCache.clear_cache()
        
        message = f"Generated {updated} encoding(s)"
        if failed:
            message += f", {failed} failed"
        
        self.message_user(request, message)
    generate_encoding.short_description = "Generate face encoding for selected faces"
    
    def clear_cache_action(self, request, queryset):
        """Clear face encoding cache"""
        FaceEncodingCache.clear_cache()
        self.message_user(request, "Face encoding cache cleared")
    clear_cache_action.short_description = "Clear encoding cache"


# Register the admin
admin.site.register(Faces, FacesAdmin)
