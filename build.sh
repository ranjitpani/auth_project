#!/usr/bin/env bash

python manage.py migrate

echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(email='admin@gmail.com').exists() or \
User.objects.create_superuser(email='admin@gmail.com', password='Admin@123')" | python manage.py shell