# IP Tracking System

A comprehensive Django-based IP tracking and security monitoring system.

## Features

- IP request logging and analytics
- IP blacklisting and access control
- Geolocation tracking
- Rate limiting
- Anomaly detection
- REST API with Swagger documentation
- Celery background tasks
- Email notifications

## Deployment

The application is configured for deployment on Render.com with:
- Web service (Django + Gunicorn)
- Celery worker for background tasks
- Redis for caching and message broker
- PostgreSQL database

## API Documentation

Access the Swagger documentation at `/swagger/` after deployment.

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Run migrations: `python manage.py migrate`
5. Start development server: `python manage.py runserver`