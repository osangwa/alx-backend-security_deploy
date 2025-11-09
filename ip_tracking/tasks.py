from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import RequestLog, SuspiciousIP, BlockedIP, IPGeolocation
import requests
import logging

logger = logging.getLogger(__name__)

@shared_task
def detect_suspicious_activity():
    """Detect suspicious IP activity"""
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    try:
        # High volume detection
        high_volume_ips = RequestLog.objects.filter(
            timestamp__gte=one_hour_ago
        ).values('ip_address').annotate(
            request_count=Count('id')
        ).filter(request_count__gt=100)
        
        for ip_data in high_volume_ips:
            ip_address = ip_data['ip_address']
            request_count = ip_data['request_count']
            
            SuspiciousIP.objects.update_or_create(
                ip_address=ip_address,
                defaults={
                    'reason': f'High request volume: {request_count} requests in 1 hour',
                    'is_active': True,
                    'request_count': request_count
                }
            )
        
        # Sensitive path access detection
        sensitive_paths = ['/admin/', '/login/', '/api/auth/', '/reset-password/']
        sensitive_access = RequestLog.objects.filter(
            timestamp__gte=one_hour_ago,
            path__in=sensitive_paths
        ).values('ip_address').annotate(
            access_count=Count('id')
        ).filter(access_count__gt=10)
        
        for access_data in sensitive_access:
            ip_address = access_data['ip_address']
            access_count = access_data['access_count']
            
            paths_accessed = RequestLog.objects.filter(
                ip_address=ip_address,
                timestamp__gte=one_hour_ago,
                path__in=sensitive_paths
            ).values_list('path', flat=True).distinct()
            
            SuspiciousIP.objects.update_or_create(
                ip_address=ip_address,
                defaults={
                    'reason': f'Excessive access to sensitive paths: {list(paths_accessed)}',
                    'is_active': True,
                    'request_count': access_count
                }
            )
        
        logger.info(f"Detected {len(high_volume_ips)} high-volume IPs and {len(sensitive_access)} suspicious access patterns")
        return f"Detected {len(high_volume_ips) + len(sensitive_access)} suspicious activities"
    
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        return f"Detection failed: {str(e)}"

@shared_task
def cleanup_old_logs():
    """Clean up old request logs"""
    try:
        retention_days = 30
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        deleted_count = RequestLog.objects.filter(timestamp__lt=cutoff_date).delete()[0]
        logger.info(f"Cleaned up {deleted_count} old request logs")
        return f"Cleaned up {deleted_count} logs"
    except Exception as e:
        logger.error(f"Log cleanup failed: {e}")
        return f"Cleanup failed: {str(e)}"

@shared_task
def send_daily_security_report():
    """Send daily security report"""
    try:
        yesterday = timezone.now() - timedelta(days=1)
        
        stats = {
            'total_requests': RequestLog.objects.filter(timestamp__gte=yesterday).count(),
            'blocked_attempts': RequestLog.objects.filter(
                timestamp__gte=yesterday,
                ip_address__in=BlockedIP.objects.values_list('ip_address', flat=True)
            ).count(),
            'new_suspicious_ips': SuspiciousIP.objects.filter(detected_at__gte=yesterday).count(),
            'date': timezone.now().strftime('%Y-%m-%d'),
        }
        
        subject = f"Daily Security Report - {stats['date']}"
        html_message = render_to_string('emails/daily_security_report.html', {'stats': stats})
        
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@yourapp.com')
        
        send_mail(
            subject=subject,
            message='Please view this email in HTML format',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html_message
        )
        
        return "Daily security report sent"
    except Exception as e:
        logger.error(f"Failed to send security report: {e}")
        return f"Report failed: {str(e)}"

@shared_task
def get_ip_geolocation(ip_address):
    """Get geolocation data for IP"""
    try:
        # Check cache first
        from django.core.cache import cache
        cache_key = f"geo_{ip_address}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Query external API
        response = requests.get(f'http://ipapi.co/{ip_address}/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            geolocation_data = {
                'ip': ip_address,
                'country': data.get('country_name', ''),
                'city': data.get('city', ''),
                'region': data.get('region', ''),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('timezone', ''),
            }
            
            # Cache for 24 hours
            cache.set(cache_key, geolocation_data, 86400)
            
            # Save to database
            IPGeolocation.objects.update_or_create(
                ip_address=ip_address,
                defaults={
                    'country': geolocation_data['country'],
                    'city': geolocation_data['city'],
                    'region': geolocation_data['region'],
                    'latitude': geolocation_data['latitude'],
                    'longitude': geolocation_data['longitude'],
                    'timezone': geolocation_data['timezone'],
                }
            )
            
            return geolocation_data
        
        return {'ip': ip_address, 'error': 'Geolocation unavailable'}
    except Exception as e:
        logger.error(f"Geolocation failed for {ip_address}: {e}")
        return {'ip': ip_address, 'error': str(e)}

@shared_task
def send_test_email(email):
    """Send test email"""
    try:
        subject = 'Test Email - IP Tracking System'
        message = 'This is a test email from your IP Tracking System.'
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email]
        )
        
        return f"Test email sent to {email}"
    except Exception as e:
        logger.error(f"Test email failed: {e}")
        return f"Email failed: {str(e)}"