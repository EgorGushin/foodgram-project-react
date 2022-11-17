#!/bin/bash

if [ "$SQL_DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    while ! nc -z $SQL_HOST $SQL_PORT; do
      echo "[x] Waiting PG service"
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

python manage.py makemigrations
python manage.py migrate --no-input
python manage.py collectstatic --no-input
python manage.py loaddata infra/fixtures.json

python -c "import django; django.setup(); \
    from django.contrib.auth.management.commands.createsuperuser import get_user_model; \
    get_user_model()._default_manager.db_manager('default').create_superuser( \
    email='$DJANGO_SU_EMAIL', \
    username='$DJANGO_SU_USERNAME', \
    first_name='$DJANGO_SU_FIRST_NAME', \
    last_name='$DJANGO_SU_LAST_NAME', \
    password='$DJANGO_SU_PASSWORD')"

exec "$@"