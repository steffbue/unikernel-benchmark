#!/bin/bash

cd /usr/src/aws/config

# Create role for importing the OSv image
aws iam create-role --role-name vmimport --assume-role-policy-document "file://vmimport-trust-policy.json"
aws iam put-role-policy --role-name vmimport --policy-name vmimport --policy-document "file://vmimport-role-policy.json"

# Create role for granting S3 Access to EC2 Instances
aws iam create-role --role-name s3access --assume-role-policy-document "file://ec2role-trust-policy.json"
aws iam put-role-policy --role-name s3access --policy-name S3ReadAccess --policy-document "file://ec2role-role-policy.json"
aws iam create-instance-profile --instance-profile-name s3access-profile
aws iam add-role-to-instance-profile --instance-profile-name s3access-profile --role-name s3access