#!/bin/bash
# Устанавливаем строгий режим
set -e

# Ожидание доступности базы данных
./wait-for-it.sh db:5432 -t 60 -- echo "PostgreSQL is ready"

# Собираем статичные файлы в одно место
python manage.py collectstatic --noinput

# Применение миграций, если это необходимо
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py admininit

# Внесение демонстрационных данных
python manage.py loaddata example_fixture.json

# Запуск Django приложения
exec "$@"
