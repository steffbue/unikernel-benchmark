#!/bin/bash

cd /root/.capstan/instances/qemu/DummyBackend/
aws s3api create-bucket --bucket osvimport --region $AWS_DEFAULT_REGION --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION
aws s3 cp disk.vhd s3://osvimport/