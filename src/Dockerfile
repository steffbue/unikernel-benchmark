FROM ubuntu:focal

RUN apt update

RUN apt install -y curl
RUN curl https://raw.githubusercontent.com/cloudius-systems/capstan/master/scripts/download | bash

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt -y install nodejs

RUN apt install -y qemu-utils qemu-system

RUN apt install -y unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

RUN apt install -y less

RUN apt install -y python3-pip

RUN apt install -y openssh-client

RUN pip3 install boto3
RUN pip3 install requests
RUN pip3 install matplotlib

COPY scripts /usr/src/scripts
COPY backend /usr/src/backend_osv
COPY backend /usr/src/backend_linux
COPY control_backend /usr/src/control_backend
COPY aws /usr/src/aws
COPY osv /usr/src/osv

WORKDIR /usr/src/scripts
RUN chmod -R +x .
CMD python3 prepare-benchmark.py
