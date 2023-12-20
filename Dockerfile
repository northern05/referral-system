FROM python:3.9.7

WORKDIR /usr/src/app

# install dependencies
RUN apt-get update && apt-get upgrade -y
RUN pip install --upgrade pip
RUN apt-get install dnsutils -y
RUN apt-get install cron -y

COPY . /usr/src/app/

RUN pip install --no-cache-dir --force-reinstall -r requirements.txt

ARG LISTEN_PORT
ENV LISTEN_PORT=${LISTEN_PORT}
EXPOSE ${LISTEN_PORT}
