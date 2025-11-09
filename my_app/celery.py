import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

app = Celery('your_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'detect-suspicious-activity-hourly': {
        'task': 'ip_tracking.tasks.detect_suspicious_activity',
        'schedule': 3600.0,
    },
    'cleanup-old-logs-daily': {
        'task': 'ip_tracking.tasks.cleanup_old_logs',
        'schedule': 86400.0,
    },
    'send-daily-reports': {
        'task': 'ip_tracking.tasks.send_daily_security_report',
        'schedule': 86400.0,
    },
}

app.conf.timezone = 'UTC'