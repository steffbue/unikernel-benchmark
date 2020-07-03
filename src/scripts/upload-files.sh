#!/bin/bash


# Upload OSv image to S3
cd /root/.capstan/instances/qemu/DummyBackend
aws s3api create-bucket --bucket osvimport --region $AWS_DEFAULT_REGION --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION
aws s3 cp disk.vhd s3://osvimport 


# Upload Linux backend to S3
cd /usr/src
tar -zcvf backend.tar.gz backend_linux
aws s3api create-bucket --bucket linuxbackend --region $AWS_DEFAULT_REGION --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION
aws s3 cp backend.tar.gz s3://linuxbackend
cd /usr/src/aws/config

# Upload Control backends to S3 (used for boot time metric)
tar -zcvf linux.tar.gz control_backend/linux
tar -zcvf osv.tar.gz control_backend/osv
aws s3api create-bucket --bucket controlbackend --region $AWS_DEFAULT_REGION --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION
aws s3 cp linux.tar.gz s3://controlbackend
aws s3 cp osv.tar.gz s3://controlbackend

