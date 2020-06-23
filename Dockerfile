FROM ubuntu:focal

RUN apt update

RUN apt install -y curl
RUN curl https://raw.githubusercontent.com/cloudius-systems/capstan/master/scripts/download | bash

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt -y install nodejs


COPY backend /usr/src/backend
COPY scripts /usr/src/scripts

WORKDIR /usr/src/backend
RUN npm install

WORKDIR /usr/src/scripts
RUN chmod -R +x .
CMD while true; do sleep 2; done
