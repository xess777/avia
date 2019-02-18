FROM python:3.7-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip && \
    pip install pipenv
COPY . /usr/src/app

WORKDIR /usr/src/app/
RUN pipenv install --skip-lock --system --dev
WORKDIR /usr/src/app/src

ENTRYPOINT ["gunicorn", "app:get_app()", "--bind", "0.0.0.0:80", "--preload"]
