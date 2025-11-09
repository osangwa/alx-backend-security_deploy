from django.contrib import admin
from .models import RequestLog, BlockedIP, SuspiciousIP, IPGeolocation

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'path', 'method', 'country', 'timestamp']
    list_filter = ['method', 'country', 'timestamp']
    search_fields = ['ip_address', 'path']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'is_active', 'created_at', 'reason']
    list_filter = ['is_active', 'created_at']
    search_fields = ['ip_address', 'reason']
    actions = ['activate', 'deactivate']
    
    def activate(self, request, queryset):
        queryset.update(is_active=True)
    activate.short_description = "Activate selected IP blocks"
    
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
    deactivate.short_description = "Deactivate selected IP blocks"

@admin.register(SuspiciousIP)
class SuspiciousIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'is_active', 'detected_at', 'request_count']
    list_filter = ['is_active', 'detected_at']
    search_fields = ['ip_address', 'reason']
    readonly_fields = ['detected_at']

@admin.register(IPGeolocation)
class IPGeolocationAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'country', 'city', 'last_updated']
    list_filter = ['country']
    search_fields = ['ip_address', 'country', 'city']
    readonly_fields = ['last_updated']