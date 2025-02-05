FROM python:3.12

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y python3-tk

WORKDIR /app


RUN pip install poetry
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY mysite .

RUN python manage.py collectstatic --noinput


EXPOSE 8080