from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'request-logs', views.RequestLogViewSet)
router.register(r'blocked-ips', views.BlockedIPViewSet)
router.register(r'suspicious-ips', views.SuspiciousIPViewSet)
router.register(r'geolocations', views.IPGeolocationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', views.IPStatsView.as_view(), name='ip-stats'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('geolocation/<str:ip_address>/', views.IPGeolocationLookupView.as_view(), name='ip-geolocation'),
    path('notifications/test-email/', views.TestEmailView.as_view(), name='test-email'),
]