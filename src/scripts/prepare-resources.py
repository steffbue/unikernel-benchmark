import json
import os
import boto3
from botocore.exceptions import ClientError

iam_client = boto3.client('iam')
ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

tag = {'Key': 'Benchmark', 'Value': 'Unikernel'}

def upload_osvimage_s3(s3_client, s3_resource):
    os.chdir('/root/.capstan/instances/qemu/DummyBackend')

    s3_client.create_bucket(Bucket='osvimport', CreateBucketConfiguration={'LocationConstraint': os.environ['AWS_DEFAULT_REGION']})
    bucket = s3_resource.Bucket('osvimport')
    bucket.upload_file('disk.vhd', 'disk.vhd')
    return

def import_osvimage_snapshot(ec2_client, ec2_resource):
    os.chdir('/usr/src/aws/config')

    with open('container.json', 'r') as container_file:
        container_json = json.load(container_file)
        snapshot = ec2_client.import_snapshot(Description='OSv Image', DiskContainer=container_json, RoleName='vmimport')
        container_file.close()
    return


try:
    upload_osvimage_s3(s3_client, s3_resource)
    import_osvimage_snapshot(ec2_client, ec2_resource)
    
except ClientError as e:
    print(e)
    exit(1)