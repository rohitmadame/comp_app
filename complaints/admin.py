from django.contrib import admin
from django.utils.html import format_html
from .models import Complaint, ComplaintImage

class ComplaintImageInline(admin.TabularInline):
    model = ComplaintImage
    extra = 1
    readonly_fields = ('image_preview',)
    fields = ('image', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; border-radius: 4px;">',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = "Preview"

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'status_badge', 
        'get_complaint_type_display',  # Use display method for choice field
        'city_ward',
        'user',
        'image_gallery',
        'created_at'
    )
    list_editable = ()
    list_filter = (
        'status', 
        'complaint_type', 
        'city'
    )
    search_fields = ('city', 'ward_number', 'description')
    inlines = [ComplaintImageInline]
    readonly_fields = ('image_gallery',)

    # Correct field references
    def get_complaint_type_display(self, obj):
        return obj.get_complaint_type_display()
    get_complaint_type_display.short_description = "Complaint Type"

    def city_ward(self, obj):
        return f"{obj.city} (Ward {obj.ward_number})"
    city_ward.short_description = "Location"
    
    def image_gallery(self, obj):
        images = obj.images.all()[:3]
        return format_html(" ".join(
            f'<img src="{img.image.url}" style="max-height: 50px; margin-right: 5px;">' 
            for img in images
        )) if images else "No images"
    image_gallery.short_description = "Attachments"

    def status_badge(self, obj):
        color = {
            'pending': 'orange', 
            'in_progress': 'blue',
            'resolved': 'green'
        }.get(obj.status, 'gray')
        return format_html(
            '<span style="color: white; background: {color}; padding: 2px 8px; border-radius: 10px;">{status}</span>',
            color=color,
            status=obj.get_status_display()
        )
    status_badge.short_description = "Status"

@admin.register(ComplaintImage)
class ComplaintImageAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        return format_html(
            '<img src="{}" style="max-height: 200px;">',
            obj.image.url
        )
    image_preview.short_description = "Preview"