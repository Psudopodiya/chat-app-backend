Django Channels: Access it at http://localhost:8000
Django Admin Panel: Access it at http://localhost:8001/admin


first time:
    docker-compose build
    docker-compose run admin python manage.py migrate
    docker-compose run admin python manage.py showmigrations
    docker-compose run admin python manage.py createsuperuser
    docker-compose run admin python manage.py collectstatic --no-input
    docker-compose up
