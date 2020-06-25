import logging
import boto3
import os
import sys
import json
from botocore.exceptions import ClientError

try:
    default_region = os.environ['AWS_DEFAULT_REGION']
except KeyError:
    print('Specify AWS_DEFAULT_REGION as environment variable')
    sys.exit(1)


s3_client = boto3.client('s3', region_name=default_region)
iam_client = boto3.client('iam')
ec2_client = boto3.client('ec2')

location = {'LocationContraint': default_region}
bucket_name = 'osvimport'

try:
    s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    s3_client.upload_file(osv.path.join('/root/.capstan/instances/qemu/DummyBackend', disk.vmdk),bucket_name)
except ClientError as e:
    logging.error(e)
    sys.exit(1)

with open('/usr/src/aws/config/trust-policy.json') as trust_policy_file:
    iam_client.create_role(RoleName='vmimport', AssumeRolePolicyDocument=json.load(trust_policy_file))


with open('/usr/src/aws/config/role-policy.json') as role_policy_file:
    iam_client.put_role_policy(RoleName='vmimport', PolicyName="vmimport", PolicyDocument=json.load(role_policy_file))

with open('usr/src/aws/config/containers.json') as containers_file:
    ec2_client.import_image(Description='OSv Backend AMI', DiskContainers=json.load(containers_file))



