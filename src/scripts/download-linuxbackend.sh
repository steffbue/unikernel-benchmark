#!/bin/bash

aws s3 cp s3://linuxbackend/backend.tar.gz backend.tar.gz
tar -xf backend.tar.gz backend
cd backend
chmod +x config.sh
chmod +x run.sh
./config.sh