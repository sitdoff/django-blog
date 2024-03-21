FROM python:3.12-alpine

LABEL creator="Roman Ivanov"
LABEL email="sitdoff@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.6.1

WORKDIR /code

COPY poetry.lock pyproject.toml wait-for-it.sh entrypoint.sh .env uwsgi.ini ./project /code/

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && apk update \
    && apk add python3-dev build-base linux-headers pcre-dev bash --no-cache --upgrade\
    && poetry config virtualenvs.create false \
    && poetry install \
    && chmod +x /code/entrypoint.sh

CMD ["uwsgi", "--ini", "uwsgi.ini"]

