FROM python:3.10

WORKDIR /usr/src/app

# install dependencies
RUN apt-get update && apt-get upgrade -y
RUN pip install --upgrade pip
RUN apt-get install cron -y
RUN apt-get install dnsutils -y
RUN pip install gunicorn

COPY . /usr/src/app/

RUN pip install --no-cache-dir --force-reinstall -r requirements.txt

ENV FLASK_APP app.py

ARG LISTEN_PORT
ENV LISTEN_PORT=${LISTEN_PORT}
