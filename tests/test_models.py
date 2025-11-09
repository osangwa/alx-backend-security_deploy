from django.test import TestCase
from django.utils import timezone
from ip_tracking.models import RequestLog, BlockedIP, SuspiciousIP

class ModelTests(TestCase):
    def test_request_log_creation(self):
        log = RequestLog.objects.create(
            ip_address='192.168.1.1',
            path='/test/',
            method='GET'
        )
        self.assertEqual(str(log), '192.168.1.1 - /test/')
    
    def test_blocked_ip_creation(self):
        blocked = BlockedIP.objects.create(
            ip_address='10.0.0.1',
            reason='Test blocking'
        )
        self.assertTrue(blocked.is_active)
        self.assertEqual(str(blocked), '10.0.0.1 - Test blocking')