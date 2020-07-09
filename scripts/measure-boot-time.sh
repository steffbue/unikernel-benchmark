#!/bin/bash

cd ../src
sudo docker build -t unikernel-benchmark .

cd results
sudo docker run -it -v $(pwd):/usr/src/results -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION unikernel-benchmark python3 measure-boot-time.py