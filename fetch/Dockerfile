FROM python:3.8
# RUN apt update && apt upgrade -y 
# RUN apt install software-properties-common -y
# RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update && apt upgrade -y 
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
ENV LANG=C.UTF-8
RUN apt-get install build-essential \
      postgresql gcc python3-dev musl-dev \
      libssl-dev libffi-dev unixodbc-dev \
      libpq-dev -y
RUN pip3 install pipenv 

RUN mkdir app
COPY Pipfile /app
WORKDIR /app
RUN pipenv install --skip-lock
COPY . /app
CMD ["python3","-u","app.py"]
