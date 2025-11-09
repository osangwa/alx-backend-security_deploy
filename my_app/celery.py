import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ip_tracking.settings')

app = Celery('ip_tracking')

# Using Redis as broker (PythonAnywhere provides Redis)
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

app.conf.beat_schedule = {
    'detect-suspicious-activity-hourly': {
        'task': 'ip_tracking.tasks.detect_suspicious_activity',
        'schedule': 3600.0,
    },
    'cleanup-old-logs-daily': {
        'task': 'ip_tracking.tasks.cleanup_old_logs',
        'schedule': 86400.0,
    },
}