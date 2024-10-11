#!/bin/bash
# Create a superuser for the Django admin
docker-compose exec web python manage.py createsuperuser