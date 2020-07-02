import os
import boto3
from botocore.exceptions import ClientError


ec2_client = boto3.client('ec2')

def create_text_file_with_ip(path, public_ip):
    os.chdir(path)
    with open(os.path.join(path,'ip-info.txt'), 'w') as output_file:
        output_file.write(public_ip)
        output_file.close()
    return


try:
    allocation = ec2_client.allocate_address()
    ec2_client.create_tags(Resources=[allocation['AllocationId']], Tags=[{'Key': 'Benchmark', 'Value': 'Unikernel'}])
    public_ip = allocation['PublicIp']
    print(public_ip)
    create_text_file_with_ip('/usr/src/backend_osv', public_ip)
    create_text_file_with_ip('/usr/src/backend_linux', public_ip)
except ClientError as e:
    print(e)
    exit(1)