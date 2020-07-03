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
    
    SSHPermission = {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    DebugPermission = {'IpProtocol': 'tcp', 'FromPort': 8080, 'ToPort': 8080, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}

    ec2_client.authorize_security_group_ingress(GroupId=sec_grp_id, IpPermissions=[SSHPermission, DebugPermission])
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

def prepare_linux_instance(ec2_client, ec2_resource, key_name, secgroup_id, iam_instance_profile, user_data_filename, instance_tags):
    ami_id = 'ami-0a02ee601d742e89f'

    os.chdir('/usr/src/scripts')
    user_data_file = open(user_data_filename, 'r')
    user_data = user_data_file.read()
    user_data_file.close()

    resp_instance = ec2_resource.create_instances(ImageId=ami_id, InstanceType='t2.micro', KeyName=key_name, SecurityGroupIds=[secgroup_id], MinCount=1, MaxCount=1, IamInstanceProfile=iam_instance_profile, UserData=user_data)
    instance_id = resp_instance[0].id
    ec2_resource.create_tags(Resources=[instance_id], Tags=instance_tags)
    instance = ec2_resource.Instance(id=instance_id)
    instance.wait_until_running()

    # Time for UserData script to prepare instance
    time.sleep(120)
    
    #Stopping instance
    instance.stop()

    return instance_id

def prepare_linux_benchmark_instance(ec2_client, ec2_resource, key_name, secgroup_id, iam_instance_profile):
    prepare_linux_instance(ec2_client, ec2_resource, key_name, secgroup_id, iam_instance_profile, 'userdata-linuxbackend.sh', Tags=[{'Key':'Benchmark', 'Value':'Unikernel'}, {'Key': 'Type', 'Value': 'Linux'}])
    return

def prepare_control_instance_for_linux_benchmark(ec2_client, ec2_resource, key_name, secgroup_id, iam_instance_profile):
    instance_id = prepare_linux_instance(ec2_client, ec2_resource, key_name, secgroup_id, iam_instance_profile, 'userdata-controlbackend-linux.sh', Tags=[{'Key':'Benchmark', 'Value':'Unikernel'}, {'Key': 'Type', 'Value': 'Control-Linux'}])
    response = ec2_client.describe_addresses(Filters=[{'Name': 'tag:Benchmark', 'Values': ['Unikernel']}, {'Name': 'tag:Type', 'Values': ['Control-Linux']}])
    allocation_id = response['Addresses'][0]['AllocationId']
    ec2_client.associate_address(AllocationId=allocation_id, InstanceId=instance_id)
    return


def prepare_control_instance_for_osv_benchmark(ec2_client, ec2_resource, key_name, secgroup_id, iam_instance_profile):
    instance_id = prepare_linux_instance(ec2_client, ec2_resource, key_name, secgroup_id, iam_instance_profile, 'userdata-controlbackend-osv.sh', Tags=[{'Key':'Benchmark', 'Value':'Unikernel'}, {'Key': 'Type', 'Value': 'Control-OSV'}])
    response = ec2_client.describe_addresses(Filters=[{'Name': 'tag:Benchmark', 'Values': ['Unikernel']}, {'Name': 'tag:Type', 'Values': ['Control-OSV']}])
    allocation_id = response['Addresses'][0]['AllocationId']
    ec2_client.associate_address(AllocationId=allocation_id, InstanceId=instance_id)
    return


ec2_client_t1 = boto3.session.Session().client('ec2')
ec2_client_t2 = boto3.session.Session().client('ec2')
ec2_client_t3 = boto3.session.Session().client('ec2')
ec2_client_t4 = boto3.session.Session().client('ec2')
ec2_resource_t1 = boto3.session.Session().resource('ec2')
ec2_resource_t2 = boto3.session.Session().resource('ec2')
ec2_resource_t3 = boto3.session.Session().resource('ec2')
ec2_resource_t4 = boto3.session.Session().resource('ec2')
iam_client = boto3.client('iam')

try:
    key_name, key_material = create_benchmark_keypair(ec2_client_t1, ec2_resource_t1)
    secgroup_id = create_and_authorize_benchmark_security_group(ec2_client_t1, ec2_resource_t1)
    
    resp_instance_profile = iam_client.get_instance_profile(InstanceProfileName='s3access-profile')
    iam_instance_profile = {'Arn': resp_instance_profile['InstanceProfile']['Arn']}


    t1 = threading.Thread(target=prepare_osv_benchmark_instance, args=(ec2_client_t1, ec2_resource_t1, key_name, secgroup_id))
    t2 = threading.Thread(target=prepare_linux_benchmark_instance, args=(ec2_client_t2, ec2_resource_t2, key_name, secgroup_id, iam_instance_profile))
    t3 = threading.Thread(target=prepare_control_instance_for_linux_benchmark, args=(ec2_client_t3, ec2_resource_t3, key_name, secgroup_id, iam_instance_profile))
    t4 = threading.Thread(target=prepare_control_instance_for_osv_benchmark, args=(ec2_client_t4, ec2_resource_t4, key_name, secgroup_id, iam_instance_profile))
    
    t1.start()
    t2.start()
    t3.start()
    t4.start()


    t1.join()
    t2.join()
    t3.join()
    t4.join()
    
    

except ClientError as e:
    print(e)
    exit(1)

