#!/bin/bash

aws s3 s3://linuxbackend/backend.tar.gz backend.tar.gz
tar -xcvf backend.tar.gz backend_linux
chmod +x config.sh
./config.sh