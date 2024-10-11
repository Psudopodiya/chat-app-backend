#!/bin/bash
# Run database migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate