FROM ubuntu:focal

RUN apt update

RUN apt install -y curl
RUN curl https://raw.githubusercontent.com/cloudius-systems/capstan/master/scripts/download | bash

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt -y install nodejs

RUN apt install -y qemu-utils

RUN apt install -y unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

RUN apt install -y less


COPY backend /usr/src/backend
COPY scripts /usr/src/scripts
COPY config /usr/src/config

WORKDIR /usr/src/backend
RUN npm install

WORKDIR /usr/src/scripts
RUN chmod -R +x .
CMD while true; do sleep 2; done
