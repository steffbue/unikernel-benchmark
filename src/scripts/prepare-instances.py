import os
import time
import subprocess
import threading
import boto3
import boto3.session
from botocore.exceptions import ClientError



def create_benchmark_keypair(ec2_client, ec2_resource):
    resp_keypair = ec2_client.create_key_pair(KeyName="benchmark-key")
    print(resp_keypair)
    ec2_resource.create_tags(Resources=[resp_keypair['KeyPairId']], Tags=[{'Key':'Benchmark', 'Value':'Unikernel'}])
    return resp_keypair['KeyName'], resp_keypair['KeyMaterial']

def create_and_authorize_benchmark_security_group(ec2_client, ec2_resource):
    resp_secgrp = ec2_client.create_security_group(GroupName="security-group-benchmark", Description="security-group-benchmark")
    sec_grp_id = resp_secgrp['GroupId']
    ec2_resource.create_tags(Resources=[sec_grp_id], Tags=[{'Key':'Benchmark', 'Value':'Unikernel'}])
    
    HTTPPermission = {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    SSHPermission = {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    DebugPermission = {'IpProtocol': 'tcp', 'FromPort': 8080, 'ToPort': 8080, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}

    ec2_client.authorize_security_group_ingress(GroupId=sec_grp_id, IpPermissions=[HTTPPermission, SSHPermission, DebugPermission])
    return sec_grp_id
    

def prepare_osv_benchmark_instance(ec2_client, ec2_resource, key_name, secgroup_id):
    resp_ami = ec2_client.describe_images(Filters=[{'Name': 'name', 'Values': ['OSv Image']}], Owners=['self'])
    ami_id = resp_ami['Images'][0]['ImageId']
    resp_instance = ec2_resource.create_instances(ImageId=ami_id, InstanceType='t2.micro', KeyName=key_name, SecurityGroupIds=[secgroup_id], MinCount=1, MaxCount=1)
    instance_id = resp_instance[0].id
    ec2_resource.create_tags(Resources=[instance_id], Tags=[{'Key':'Benchmark', 'Value':'Unikernel'}])
    instance = ec2_resource.Instance(id=instance_id)
    instance.wait_until_running()
    instance.stop()

    return instance_id

def prepare_linux_benchmark_instance(ec2_client, ec2_resource, key_name, secgroup_id, iam_instance_profile):
    ami_id = 'ami-0a02ee601d742e89f'

    os.chdir('/usr/src/scripts')
    download_file = open('download-linuxbackend.sh', 'r')
    user_data = download_file.read()
    download_file.close()

    resp_instance = ec2_resource.create_instances(ImageId=ami_id, InstanceType='t2.micro', KeyName=key_name, SecurityGroupIds=[secgroup_id], MinCount=1, MaxCount=1, IamInstanceProfile=iam_instance_profile, UserData=user_data)
    instance_id = resp_instance[0].id
    ec2_resource.create_tags(Resources=[instance_id], Tags=[{'Key':'Benchmark', 'Value':'Unikernel'}])
    instance = ec2_resource.Instance(id=instance_id)
    instance.wait_until_running()

    # Time for UserData script to prepare instance
    time.sleep(120)
    
    #Stopping instance
    instance.stop()
    

ec2_client1 = boto3.session.Session().client('ec2')
ec2_client2 = boto3.session.Session().client('ec2')
ec2_resource1 = boto3.session.Session().resource('ec2')
ec2_resource2 = boto3.session.Session().resource('ec2')
iam_client = boto3.client('iam')

try:
    key_name, key_material = create_benchmark_keypair(ec2_client1, ec2_resource1)
    secgroup_id = create_and_authorize_benchmark_security_group(ec2_client1, ec2_resource1)
    
    resp_instance_profile = iam_client.get_instance_profile(InstanceProfileName='s3access-profile')
    iam_instance_profile = {'Arn': resp_instance_profile['InstanceProfile']['Arn']}


    #t1 = threading.Thread(target=prepare_osv_benchmark_instance, args=(ec2_client1, ec2_resource1, key_name, secgroup_id))
    t2 = threading.Thread(target=prepare_linux_benchmark_instance, args=(ec2_client2, ec2_resource2, key_name, secgroup_id, iam_instance_profile))
    #t1.start()
    t2.start()

    #t1.join()
    t2.join()

    
    

except ClientError as e:
    print(e)
    exit(1)

