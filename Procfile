web: gunicorn your_project.wsgi:application
worker: celery -A your_project worker --loglevel=info
beat: celery -A your_project beat --loglevel=info