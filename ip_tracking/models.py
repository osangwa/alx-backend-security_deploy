from django.db import models

class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10, default='GET')
    user_agent = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    status_code = models.IntegerField(default=200)
    
    class Meta:
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['path']),
            models.Index(fields=['country']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.ip_address} - {self.path} - {self.timestamp}"

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason}"

class SuspiciousIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    request_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Suspicious IP"
        verbose_name_plural = "Suspicious IPs"
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason}"

class IPGeolocation(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "IP Geolocation"
        verbose_name_plural = "IP Geolocations"
    
    def __str__(self):
        return f"{self.ip_address} - {self.country}, {self.city}"