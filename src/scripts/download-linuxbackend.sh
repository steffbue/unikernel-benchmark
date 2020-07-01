#!/bin/bash

aws s3 cp s3://linuxbackend/backend.tar.gz backend.tar.gz
aws s3 cp s3://linuxbackend/nodeserver.service nodeserver.service
tar -xf backend.tar.gz backend_linux
cp nodeserver.service /etc/systemd/system/nodeserver.service
cd backend_linux
chmod +x config.sh
./config.sh