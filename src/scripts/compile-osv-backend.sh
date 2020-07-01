#!/bin/bash

cd /usr/src/backend_osv
npm install
/root/bin/capstan package init --name "DummyBackend" --title "DummyBackend" --author "Steffen" --require osv.node-js
cp /usr/src/osv/config/run.yaml meta/run.yaml

cd /root
mkdir -p .capstan/repository/osv-loader
cd /root/.capstan/repository/osv-loader
cp -r /usr/src/osv/base_img/* .

cd /usr/src/backend_osv
/root/bin/capstan package compose DummyBackend --pull-missing
timeout 10s /root/bin/capstan run DummyBackend

cd /root/.capstan/instances/qemu/DummyBackend
qemu-img convert -f qcow2 -O vpc disk.qcow2 disk.vhd