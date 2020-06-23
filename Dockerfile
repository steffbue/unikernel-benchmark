FROM ubuntu:groovy

RUN apt update
RUN apt install -y curl
RUN curl https://raw.githubusercontent.com/cloudius-systems/capstan/master/scripts/download | bash

CMD while true; do sleep 2; done
