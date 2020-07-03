#!/bin/bash

aws s3 cp s3://linuxbackend/backend.tar.gz backend.tar.gz
tar -xf backend.tar.gz --strip-components 1
chmod +x config.sh
./config.sh