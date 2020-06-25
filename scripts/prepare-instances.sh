#!/bin/bash



cd /usr/src/backend
/root/bin/capstan package init --name "DummyBackend" --title "DummyBackend" --author "Steffen" --require osv.node-js
cp /usr/src/config/run.yaml meta/run.yaml
/root/bin/capstan package compose DummyBackend --pull-missing
/root/bin/capstan run DummyBackend

cd /root
mkdir -p .capstan/repository/osv-loader
cd .capstan/repository/osv-loader
curl https://github.com/cloudius-systems/osv/releases/download/v0.55.0/osv-loader.qemu --output osv-loader.qemu
curl https://github.com/cloudius-systems/osv/releases/download/v0.55.0/index.yaml --output index.yaml

#cd /root/.capstan/instances/qemu/DummyBackend/
#qemu-img convert -f qcow2 -O vmdk disk.qcow2 disk.vmdk
#aws s3api create-bucket --bucket osvimport --region $AWS_DEFAULT_REGION --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION
#aws s3 cp disk.vmdk s3://osvimport/

#cd /usr/src/config
#aws iam create-role --role-name vmimport --assume-role-policy-document "file://trust-policy.json"
#aws iam put-role-policy --role-name vmimport --policy-name vmimport --policy-document "file://role-policy.json"
#aws ec2 import-image --description "OSv Backend AMI" --disk-containers "file://containers.json"






