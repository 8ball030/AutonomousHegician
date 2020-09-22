FROM ubuntu:18.04
RUN apt update && apt upgrade -y 
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update && apt upgrade -y 
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get install python3.7 -y
RUN apt-get install python3-pip -y --fix-missing
RUN apt-get install postgresql gcc python3-dev musl-dev -y
RUN apt-get install build-essential libssl-dev libffi-dev python3.7-dev -y
RUN apt-get install unixodbc-dev -y
RUN apt-get install libpq-dev -y
ENV LANG=C.UTF-8
RUN pip3 install pipenv 

RUN mkdir app
COPY Pipfile /app
WORKDIR /app
RUN pipenv install --skip-lock
COPY . /app
CMD ["python3","-u","app.py"]
