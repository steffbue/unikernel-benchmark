#!/bin/bash

aws s3 cp s3://controlbackend/linux.tar.gz linux.tar.gz
tar -xf linux.tar.gz --strip-components 1
chmod +x config.sh
./config.sh