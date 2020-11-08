# FROM python:3.8

FROM python:3.8-alpine

RUN apk add --no-cache make git bash

RUN DEBIAN_FRONTEND="noninteractive" apk add tzdata

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev


ENV LANG=C.UTF-8
RUN apk add --update --no-cache py3-numpy py3-scipy py3-pillow
ENV PYTHONPATH "$PYTHONPATH:/usr/lib/python3.7/site-packages"


RUN apk add  postgresql-dev 
RUN pip3 install protobuf colorlog graphviz pipenv psycopg2-binary

# golang
RUN apk add --no-cache go


RUN mkdir app
COPY Pipfile /app
WORKDIR /app/agents
RUN pipenv install --skip-lock
WORKDIR /app
COPY . /app

CMD ["python3","-u","app.py"]
