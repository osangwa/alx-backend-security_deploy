#!/bin/bash
echo "=== Deploying to PythonAnywhere ==="

# Create necessary directories
mkdir -p staticfiles
mkdir -p media

# Install dependencies
pip install -r requirements-pa.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser if needed (uncomment if needed)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')" | python manage.py shell

echo "=== Deployment preparation complete ==="