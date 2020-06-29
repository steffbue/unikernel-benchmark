import boto3
from botocore.exceptions import ClientError


ec2_client = boto3.client('ec2')

try:
    allocation = ec2_client.allocate_address()
    ec2_client.create_tags(Resources=[allocation['AllocationId']], Tags=[{'Key': 'Benchmark', 'Value': 'Unikernel'}])
except ClientError as e:
    print(e)
    exit(1)