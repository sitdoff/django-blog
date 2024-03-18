#!/bin/bash
# Устанавливаем строгий режим
set -e

# Ожидание доступности базы данных
./wait-for-it.sh db:5432 -t 60 -- echo "PostgreSQL is ready"

# Собираем статичные файлы в одно место
python manage.py collectstatic

# Применение миграций, если это необходимо.
python manage.py makemigrations
python manage.py migrate
python manage.py admininit
python manage.py loaddata example_fixture.json # Внесение демонстрационных данных


# Запуск вашего Django приложения
exec "$@"
