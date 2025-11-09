from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, BlockedIP, SuspiciousIP, IPGeolocation
from .serializers import (
    RequestLogSerializer, BlockedIPSerializer, 
    SuspiciousIPSerializer, IPGeolocationSerializer,
    AnalyticsSerializer
)
from .tasks import detect_suspicious_activity, get_ip_geolocation, send_test_email
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

class RequestLogViewSet(viewsets.ModelViewSet):
    queryset = RequestLog.objects.all().order_by('-timestamp')
    serializer_class = RequestLogSerializer
    
    @swagger_auto_schema(
        operation_description="Get paginated request logs with filtering",
        manual_parameters=[
            openapi.Parameter('ip', openapi.IN_QUERY, description="Filter by IP address", type=openapi.TYPE_STRING),
            openapi.Parameter('path', openapi.IN_QUERY, description="Filter by path", type=openapi.TYPE_STRING),
            openapi.Parameter('country', openapi.IN_QUERY, description="Filter by country", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply filters
        ip_address = request.query_params.get('ip')
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
            
        path = request.query_params.get('path')
        if path:
            queryset = queryset.filter(path__icontains=path)
            
        country = request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get analytics for request logs",
        manual_parameters=[
            openapi.Parameter('days', openapi.IN_QUERY, description="Number of days to analyze", type=openapi.TYPE_INTEGER)
        ]
    )
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        analytics_data = {
            'total_requests': RequestLog.objects.filter(timestamp__gte=start_date).count(),
            'unique_ips': RequestLog.objects.filter(timestamp__gte=start_date).values('ip_address').distinct().count(),
            'top_paths': list(RequestLog.objects.filter(timestamp__gte=start_date)
                              .values('path')
                              .annotate(count=Count('id'))
                              .order_by('-count')[:10]),
            'top_countries': list(RequestLog.objects.filter(timestamp__gte=start_date)
                                 .exclude(country__isnull=True)
                                 .exclude(country='')
                                 .values('country')
                                 .annotate(count=Count('id'))
                                 .order_by('-count')[:10]),
            'requests_by_day': list(RequestLog.objects.filter(timestamp__gte=start_date)
                                   .extra({'date': "date(timestamp)"})
                                   .values('date')
                                   .annotate(count=Count('id'))
                                   .order_by('date')),
        }
        
        serializer = AnalyticsSerializer(analytics_data)
        return Response(serializer.data)

class BlockedIPViewSet(viewsets.ModelViewSet):
    queryset = BlockedIP.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = BlockedIPSerializer
    
    @swagger_auto_schema(
        operation_description="Block a new IP address",
        request_body=BlockedIPSerializer,
        responses={201: BlockedIPSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        blocked_ip = self.get_object()
        blocked_ip.is_active = False
        blocked_ip.save()
        return Response({'status': 'IP block deactivated'})

class SuspiciousIPViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SuspiciousIP.objects.filter(is_active=True).order_by('-detected_at')
    serializer_class = SuspiciousIPSerializer

class IPGeolocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IPGeolocation.objects.all().order_by('-last_updated')
    serializer_class = IPGeolocationSerializer

class IPStatsView(APIView):
    @swagger_auto_schema(
        operation_description="Get overall IP tracking statistics",
        responses={
            200: openapi.Response(
                description="Statistics data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_requests': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'blocked_ips_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'suspicious_ips_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'unique_countries': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            )
        }
    )
    @method_decorator(cache_page(60 * 5))
    def get(self, request):
        stats = {
            'total_requests': RequestLog.objects.count(),
            'blocked_ips_count': BlockedIP.objects.filter(is_active=True).count(),
            'suspicious_ips_count': SuspiciousIP.objects.filter(is_active=True).count(),
            'unique_countries': RequestLog.objects.exclude(country__isnull=True).exclude(country='').values('country').distinct().count(),
            'requests_today': RequestLog.objects.filter(timestamp__date=timezone.now().date()).count(),
        }
        return Response(stats)

class AnalyticsView(APIView):
    @swagger_auto_schema(
        operation_description="Get comprehensive analytics",
        manual_parameters=[
            openapi.Parameter('days', openapi.IN_QUERY, description="Number of days", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        analytics = {
            'period': f"Last {days} days",
            'requests_over_time': self.get_requests_over_time(start_date),
            'top_ips': self.get_top_ips(start_date),
            'geographic_distribution': self.get_geographic_distribution(start_date),
            'path_analysis': self.get_path_analysis(start_date),
        }
        return Response(analytics)
    
    def get_requests_over_time(self, start_date):
        return list(RequestLog.objects.filter(timestamp__gte=start_date)
                   .extra({'date': "date(timestamp)"})
                   .values('date')
                   .annotate(count=Count('id'))
                   .order_by('date'))
    
    def get_top_ips(self, start_date):
        return list(RequestLog.objects.filter(timestamp__gte=start_date)
                   .values('ip_address', 'country')
                   .annotate(count=Count('id'))
                   .order_by('-count')[:20])
    
    def get_geographic_distribution(self, start_date):
        return list(RequestLog.objects.filter(timestamp__gte=start_date)
                   .exclude(country__isnull=True)
                   .exclude(country='')
                   .values('country')
                   .annotate(count=Count('id'))
                   .order_by('-count'))
    
    def get_path_analysis(self, start_date):
        return list(RequestLog.objects.filter(timestamp__gte=start_date)
                   .values('path')
                   .annotate(count=Count('id'))
                   .order_by('-count')[:15])

class IPGeolocationLookupView(APIView):
    @swagger_auto_schema(
        operation_description="Get geolocation data for an IP address",
        responses={
            200: openapi.Response(
                description="Geolocation data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'ip': openapi.Schema(type=openapi.TYPE_STRING),
                        'country': openapi.Schema(type=openapi.TYPE_STRING),
                        'city': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def get(self, request, ip_address):
        geolocation_data = get_ip_geolocation.delay(ip_address)
        result = geolocation_data.get(timeout=10)
        return Response(result)

class TestEmailView(APIView):
    @swagger_auto_schema(
        operation_description="Send test email notification",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Recipient email'),
            }
        )
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email address required'}, status=status.HTTP_400_BAD_REQUEST)
        
        send_test_email.delay(email)
        return Response({'message': 'Test email sent successfully'})