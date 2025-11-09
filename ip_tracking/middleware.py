from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class IPTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip_address = self.get_client_ip(request)
        
        if self.is_ip_blocked(ip_address):
            logger.warning(f"Blocked request from IP: {ip_address}")
            return HttpResponseForbidden("IP address blocked")
        
        return None
    
    def process_response(self, request, response):
        if response.status_code < 400:  # Only log successful responses
            ip_address = self.get_client_ip(request)
            self.log_request_async(ip_address, request)
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_ip_blocked(self, ip_address):
        if ip_address in ['127.0.0.1', 'localhost']:
            return False
            
        cache_key = f"blocked_ip_{ip_address}"
        is_blocked = cache.get(cache_key)
        
        if is_blocked is None:
            is_blocked = BlockedIP.objects.filter(ip_address=ip_address, is_active=True).exists()
            cache.set(cache_key, is_blocked, 300)  # Cache for 5 minutes
        
        return is_blocked
    
    def log_request_async(self, ip_address, request):
        try:
            # In production, this would be handled by Celery
            RequestLog.objects.create(
                ip_address=ip_address,
                path=request.path,
                method=request.method,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to log request: {e}")