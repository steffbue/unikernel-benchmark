import boto3
from botocore.exceptions import ClientError



def create_benchmark_keypair(ec2_client):
    resp_keypair = ec2_client.create_key_pair(KeyName="benchmark-key")
    return resp_keypair['KeyPairId'], resp_keypair['KeyMaterial']

def create_and_authorize_benchmark_security_group(ec2_client):
    resp_secgrp = ec2_client.create_security_group(GroupName="security-group-benchmark", Description="security-group-benchmark")
    sec_grp_id = resp_secgrp['GroupId']
    
    HTTPPermission = {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    SSHPermission = {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    DebugPermission = {'IpProtocol': 'tcp', 'FromPort': 8080, 'ToPort': 8080, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    
    sec2_client.authorize_security_group_ingress(GroupId=sec_grp_id, IpPermissions=[HTTPPermission, SSHPermission, DebugPermission])
    return sec_grp_id

ec2_client = boto3.client('ec2')

try:
    key_pair_id, key_material = create_benchmark_keypair(ec2_client)
    sec_group_id = create_and_authorize_benchmark_security_group(ec2_client)

    

    
    

except ClientError as e:
    print(e)
    exit(1)

