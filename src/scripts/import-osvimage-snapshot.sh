#!/bin/bash

cd /usr/src/aws/config
aws ec2 import-snapshot --description "OSv Image" --disk-container "file://container.json" --tag-specifications ResourceType=import-snapshot-task,Tags=[{Key=Benchmark, Value=Unikernel}]