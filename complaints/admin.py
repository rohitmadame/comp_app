from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Complaint, ComplaintImage

class ComplaintImageInline(admin.TabularInline):
    model = ComplaintImage
    extra = 1
    readonly_fields = ('image_preview',)
    fields = ('image', 'image_preview')
    classes = ('collapse',)
    
    def image_preview(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<a href="{url}" target="_blank">'
                    '<img src="{url}" style="max-height: 100px; border-radius: 4px; border: 1px solid #ddd; padding: 2px;">'
                    '</a>',
                    url=obj.image.url
                )
            except ValueError:
                return "Image file missing"
        return "No image uploaded"
    image_preview.short_description = "Preview"

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'status_badge', 
        'formatted_complaint_type',
        'city_ward',
        'user_link',
        'image_gallery',
        'created_at'
    )
    list_filter = (
        'status', 
        'complaint_type', 
        'city'
    )
    search_fields = ('city', 'ward_number', 'description', 'user__username')
    inlines = [ComplaintImageInline]
    readonly_fields = ('image_gallery', 'created_at', 'updated_at')
    actions = ['mark_as_resolved']
    date_hierarchy = 'created_at'
    list_per_page = 25
    readonly_fields = ('image_gallery', 'created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('user', 'status')}),
        ('Complaint Details', {'fields': (
            'complaint_type', 
            'description',
            'city',
            'ward_number'
        )}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def formatted_complaint_type(self, obj):
        return obj.get_complaint_type_display().title()
    formatted_complaint_type.short_description = "Type"
    formatted_complaint_type.admin_order_field = 'complaint_type'

    def city_ward(self, obj):
        return f"{obj.city} (Ward {obj.ward_number})" if obj.ward_number else obj.city
    city_ward.short_description = "Location"
    
    def image_gallery(self, obj):
        images = obj.images.all()[:3]
        if not images:
            return "No attachments"
        return format_html(" ".join(
            f'<a href="{img.image.url}" target="_blank">'
            f'<img src="{img.image.url}" style="max-height: 50px; margin: 2px; border: 1px solid #ddd; padding: 1px;">'
            '</a>'
            for img in images
        ))
    image_gallery.short_description = "Attachments"

    def status_badge(self, obj):
        status_colors = {
            'pending': '#ffc107', 
            'in_progress': '#17a2b8',
            'resolved': '#28a745'
        }
        return format_html(
            '<div style="background: {color}; color: white; padding: 2px 8px; '
            'border-radius: 12px; display: inline-block; font-size: 0.9em;">{status}</div>',
            color=status_colors.get(obj.status, '#6c757d'),
            status=obj.get_status_display().upper()
        )
    status_badge.short_description = "Status"

    def user_link(self, obj):
        if obj.user:
            url = reverse("admin:auth_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user)
        return "Anonymous"
    user_link.short_description = "Reported By"
    user_link.admin_order_field = 'user__username'

    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f"{updated} complaint(s) marked as resolved")
    mark_as_resolved.short_description = "Mark selected complaints as resolved"

@admin.register(ComplaintImage)
class ComplaintImageAdmin(admin.ModelAdmin):
    list_display = ('complaint_link', 'uploaded_at', 'image_preview')
    readonly_fields = ('image_preview', 'uploaded_at')
    list_select_related = ('complaint',)
    search_fields = ('complaint__description',)
    date_hierarchy = 'uploaded_at'

    def complaint_link(self, obj):
        url = reverse("admin:complaints_complaint_change", args=[obj.complaint.id])
        return format_html('<a href="{}">Complaint #{}</a>', url, obj.complaint.id)
    complaint_link.short_description = "Complaint"

    def image_preview(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<a href="{url}" target="_blank">'
                    '<img src="{url}" style="max-height: 200px; border: 1px solid #ddd; padding: 3px;">'
                    '</a>',
                    url=obj.image.url
                )
            except ValueError:
                return "File missing"
        return "No image"
    image_preview.short_description = "Preview"