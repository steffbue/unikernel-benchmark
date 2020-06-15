FROM ubuntu:groovy

RUN apt update
RUN apt install -y curl
RUN curl https://raw.githubusercontent.com/cloudius-systems/capstan/master/scripts/download | bash

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip 
RUN ./aws/install

CMD while true; do sleep 2; done
