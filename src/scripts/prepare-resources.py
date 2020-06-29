import json
import os
import boto3
from botocore.exceptions import ClientError

iam_client = boto3.client('iam')
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

tag = {'Key': 'Benchmark', 'Value': 'Unikernel'}


def create_vmimport_policy(iam_client):
    os.chdir('/usr/src/aws/config')

    with open('trust-policy.json', 'r') as trust_policy_file:
        trust_policy_json = json.load(trust_policy_file)
        trust_policy_json_string = json.dumps(trust_policy_json)
        iam_client.create_role(RoleName='vmimport', AssumeRolePolicyDocument=trust_policy_json_string, Tags=[tag])
        trust_policy_file.close()
        
    with open('role-policy.json', 'r') as role_policy_file:
        role_policy_json = json.load(role_policy_file)
        role_policy_json_string = json.dumps(role_policy_json)
        iam_client.put_role_policy(RoleName='vmimport', PolicyName='vmimport', PolicyDocument=role_policy_json_string)
        role_policy_file.close()

    waiter = iam_client.get_waiter('role_exists')
    waiter.wait(RoleName='vmimport', WaiterConfig={'Delay': 20, 'MaxAttempts': 20})
    
    return

def upload_osvimage_s3(s3_client, s3_resource):
    os.chdir('/root/.capstan/instances/qemu/DummyBackend')

    s3_client.create_bucket(Bucket='osvimport', CreateBucketConfiguration={'LocationConstraint': os.environ['AWS_DEFAULT_REGION']})
    bucket = s3_resource.Bucket('osvimport')
    bucket.upload_file('disk.vhd', 'disk.vhd')
    return

def import_osvimage_snapshot(ec2_client):
    os.chdir('/usr/src/aws/config')

    with open('container.json', 'r') as container_file:
        container_json = json.load(container_file)
        snapshot = ec2_client.import_snapshot(Description='OSv Image', DiskContainer=container_json, RoleName='vmimport')
        ec2_client.create_tags(Resources=[snapshot['SnapshotId']], Tags=[tag])
        container_file.close()
    return


try:
    upload_osvimage_s3(s3_client, s3_resource)
    create_vmimport_policy(iam_client)
    import_osvimage_snapshot(ec2_client)
    
except ClientError as e:
    print(e)
    exit(1)