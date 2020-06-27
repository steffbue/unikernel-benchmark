#!/bin/bash

cd /usr/src/config
aws iam create-role --role-name vmimport --assume-role-policy-document "file://trust-policy.json"
aws iam put-role-policy --role-name vmimport --policy-name vmimport --policy-document "file://role-policy.json"
