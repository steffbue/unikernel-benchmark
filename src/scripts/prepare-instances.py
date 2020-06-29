import os
import subprocess
import threading
import boto3
import boto3.session
from botocore.exceptions import ClientError



def create_benchmark_keypair(ec2_client, ec2_resource):
    resp_keypair = ec2_client.create_key_pair(KeyName="benchmark-key")
    ec2_resource.create_tags(Resources=[resp_keypair['KeyId']], Tags=[{'Key':'Benchmark', 'Value':'Unikernel'}])
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

def create_benchmark_instance(ec2_resource, ami_id, key_name, secgroup_id):
    resp_instance = ec2_resource.create_instances(ImageId=ami_id, InstanceType='t2.micro', KeyName=key_name, SecurityGroupIds=[secgroup_id], MinCount=1, MaxCount=1)
    return resp_instance[0].id

def prepare_osv_benchmark_instance(ec2_client, ec2_resource, key_name, secgroup_id):
    resp_ami = ec2_client.describe_images(Filters=[{'Name': 'name', 'Values': ['OSv Image']}], Owners=['self'])
    ami_id = resp_ami['Images'][0]['ImageId']

    instance_id = create_benchmark_instance(ec2_resource, ami_id, key_name, secgroup_id)
    ec2_resource.create_tags(Resources=[instance_id], Tags=[{'Key':'Benchmark', 'Value':'Unikernel'}])
    instance = ec2_resource.Instance(id=instance_id)
    instance.wait_until_running()
    instance.stop()

    return instance_id

def prepare_linux_benchmark_instance(ec2_client, ec2_resource, key_name, key_material, secgroup_id):
    resp_ami = ec2_client.describe_images(Filters=[{'Name': 'description', 'Values': ['Amazon Linux 2 LTS Candidate AMI 2017.12.0.20171212.2 x86_64 HVM EBS']}], Owners=['amazon'])
    ami_id = resp_ami['Images'][0]['ImageId']
    
    instance_id = create_benchmark_instance(ec2_resource, ami_id, key_name, secgroup_id)
    ec2_resource.create_tags(Resources=[instance_id], Tags=[{'Key':'Benchmark', 'Value':'Unikernel'}])
    instance = ec2_resource.Instance(id=instance_id)
    instance.wait_until_running()

    #Connecting to instance
    with open('benchmark-key.pem', 'w+') as f:
        f.write(key_material)
        f.close()
    os.chmod('benchmark-key.pem', 400)
    subprocess.call('scp -rp -i benchmark-key.pem /usr/src/backend_linux ec2-user@{}:/home/ec2-user/'.format(instance.public_ip_address), shell=True)
    subprocess.call('scp -rp -i benchmark-key.pem /usr/src/aws/config/nodeserver.service ec2-user@{}:/etc/systemd/system/nodeserver.service'.format(instance.public_ip_address), shell=True)
    subprocess.call("ssh -i benchmark-key.pem ec2-user@{} 'cd /home/ec2-user; . ~/.nvm/nvm.sh; nvm install node; npm install'".format(instance.public_ip_address), shell=True)
    subprocess.call("ssh -i benchmark-key.pem ec2-user@{} 'cd /etc/systemd/system; systemctl enable nodeserver.service; systemctl start nodeserver.service'".format(instance.public_ip_address), shell=True)
    
    #Stopping instance
    instance.stop()
    

ec2_client1 = boto3.session.Session().client('ec2')
ec2_client2 = boto3.session.Session().client('ec2')
ec2_resource1 = boto3.session.Session().resource('ec2')
ec2_resource2 = boto3.session.Session().resource('ec2')

try:
    key_name, key_material = create_benchmark_keypair(ec2_client1, ec2_resource1)
    secgroup_id = create_and_authorize_benchmark_security_group(ec2_client1, ec2_resource1)
    
    t1 = threading.Thread(target=prepare_osv_benchmark_instance, args=(ec2_client1, ec2_resource1, key_name, secgroup_id))
    t2 = threading.Thread(target=prepare_linux_benchmark_instance, args=(ec2_client2, ec2_resource2, key_name, key_material, secgroup_id))
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    
    

except ClientError as e:
    print(e)
    exit(1)

