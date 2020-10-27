# base image
FROM ubuntu:18.04
RUN apt-get update -y
RUN apt-get upgrade -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

RUN apt-get install curl -y
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash
RUN apt-get install nodejs -y
RUN node -v
RUN npm -v

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

COPY package.json .
RUN npm install react-scripts@3.0.1 -g  --silent
RUN npm install --silent
RUN npm install -g ganache-cli
COPY . /app
ENV PATH /app/node_modules/.bin:$PATH
# start app
CMD ["ganache-cli", "--host" , "0.0.0.0", "-p", "7545",  "-s", "1"]
