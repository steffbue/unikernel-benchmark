#!/bin/bash

sleep 20s
cd /usr/src/aws/config
aws ec2 import-snapshot --description "OSv Image" --disk-container "file://container.json"