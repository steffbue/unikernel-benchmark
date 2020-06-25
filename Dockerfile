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


COPY backend /usr/src/backend_osv
COPY backend /usr/src/backend_linux
COPY scripts /usr/src/scripts
COPY aws /usr/src/aws
COPY osv /usr/src/osv

WORKDIR /usr/src/backend_osv
RUN npm install
RUN /root/bin/capstan package init --name "DummyBackend" --title "DummyBackend" --author "Steffen" --require osv.node-js
RUN cp /usr/src/osv/config/run.yaml meta/run.yaml

WORKDIR /root
RUN mkdir -p .capstan/repository/osv-loader
WORKDIR /root/.capstan/repository/osv-loader
RUN cp -r /usr/src/osv/base_img/* .

WORKDIR /usr/src/backend_osv
RUN /root/bin/capstan package compose DummyBackend --pull-missing
RUN timeout 10s /root/bin/capstan run DummyBackend; exit 0

WORKDIR /root/.capstan/instances/qemu/DummyBackend
RUN qemu-img convert -f qcow2 -O vmdk disk.qcow2 disk.vmdk

WORKDIR /usr/src/scripts
RUN chmod -R +x .
CMD while true; do sleep 2; done
