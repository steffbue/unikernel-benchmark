import boto3
from botocore.exceptions import ClientError



def create_benchmark_keypair(ec2_client):
    resp_keypair = ec2_client.create_key_pair(KeyName="benchmark-key")
    return resp_keypair['KeyName'], resp_keypair['KeyMaterial']

def create_and_authorize_benchmark_security_group(ec2_client):
    resp_secgrp = ec2_client.create_security_group(GroupName="security-group-benchmark", Description="security-group-benchmark")
    sec_grp_id = resp_secgrp['GroupId']
    
    HTTPPermission = {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    SSHPermission = {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    DebugPermission = {'IpProtocol': 'tcp', 'FromPort': 8080, 'ToPort': 8080, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}

    ec2_client.authorize_security_group_ingress(GroupId=sec_grp_id, IpPermissions=[HTTPPermission, SSHPermission, DebugPermission])
    return sec_grp_id

def create_benchmark_instance(ec2_resource, ami_id, key_name, secgroup_id):
    resp_instance = ec2_resource.create_instances(ImageId=ami_id, InstanceType='t2.micro', KeyName=key_name, SecurityGroupIds=[secgroup_id], MinCount=1, MaxCount=1)
    return resp_instance[0].id

def prepare_osv_benchmark_instance(ec2_client, ec2_resource, key_name, secgroup_id):
    resp_ami = ec2_client.describe_images(Filters=[{'Name': 'name', 'Values': ['OSv Image']}], Owners=['self'])
    ami_id = resp_ami['Images'][0]['ImageId']
    instance_id = create_benchmark_instance(ec2_resource, ami_id, key_name, secgroup_id)
    
    instance = ec2_resource.Instance(id=instance_id)
    instance.wait_until_running()
    instance.stop()
    return instance_id

def prepare_linux_benchmark_instance(ec2_client):
    resp_ami = ec2_client.describe_images(Filters=[{'Name': 'description', 'Values': ['Amazon Linux 2 LTS Candidate AMI 2017.12.0.20171212.2 x86_64 HVM EBS']}], Owners=['amazon'])
    ami_id = resp_ami['Images'][0]['ImageId']
    print(ami_id)
    #ami_id = resp_ami['Images']['ImageId']
    #create_benchmark_instance(ec2_client, ami_id, key_name, secgroup_id)

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

try:
    key_name, key_material = create_benchmark_keypair(ec2_client)
    secgroup_id = create_and_authorize_benchmark_security_group(ec2_client)
    #prepare_linux_benchmark_instance(ec2_client)
    prepare_osv_benchmark_instance(ec2_client, ec2_resource, key_name, secgroup_id)
    #prepare_linux_benchmark_instance(ec2_client, key_name, key_material, secgroup_id)
    #prepare_osv_benchmark_instance(ec2_client, key_name, secgroup_id)
    

    
    

except ClientError as e:
    print(e)
    exit(1)

