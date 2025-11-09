from rest_framework import serializers
from .models import RequestLog, BlockedIP, SuspiciousIP, IPGeolocation

class RequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLog
        fields = '__all__'
        read_only_fields = ['timestamp']

class BlockedIPSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedIP
        fields = '__all__'
        read_only_fields = ['created_at']

class SuspiciousIPSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspiciousIP
        fields = '__all__'
        read_only_fields = ['detected_at']

class IPGeolocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPGeolocation
        fields = '__all__'
        read_only_fields = ['last_updated']

class AnalyticsSerializer(serializers.Serializer):
    total_requests = serializers.IntegerField()
    unique_ips = serializers.IntegerField()
    top_paths = serializers.ListField()
    top_countries = serializers.ListField()