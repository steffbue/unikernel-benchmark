#!/bin/bash

cd ../src
sudo docker build -t unikernel-benchmark .
sudo docker run -it -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION unikernel-benchmark python3 clean-resources.py