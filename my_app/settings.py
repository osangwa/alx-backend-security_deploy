import os
from pathlib import Path

# Add at the top of your settings file
DEBUG = False

# Update ALLOWED_HOSTS for PythonAnywhere
ALLOWED_HOSTS = [
    'osangwa.pythonanywhere.com',
    'www.osangwa.pythonanywhere.com',
]

# Database configuration for PythonAnywhere
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'osangwa$ip_tracking',
        'USER': 'osangwa',
        'PASSWORD': 'your-mysql-password',
        'HOST': 'osangwa.mysql.pythonanywhere-services.com',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files (if needed)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# For PythonAnywhere, we'll use SQLite for simplicity in this example
# Comment out the MySQL config above and use this for initial deployment:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}