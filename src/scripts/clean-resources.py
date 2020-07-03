import boto3
from botocore.exceptions import ClientError


ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
iam_client = boto3.client('iam')

filter = [{'Name': 'tag:Benchmark', 'Values': ['Unikernel']}]



response = ec2_client.describe_instances(Filters=filter)
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        print('Terminating Instance ' + instance_id)
        instance = ec2_resource.Instance(instance_id)
        instance.terminate()
        instance.wait_until_terminated()
    

response = ec2_client.describe_key_pairs(Filters=filter)
for keypair in response['KeyPairs']:
    keyname = keypair['KeyName']
    print('Deleting Key ' + keyname)
    ec2_client.delete_key_pair(KeyName=keyname)

response = ec2_client.describe_security_groups(Filters=filter)
for secgrp in response['SecurityGroups']:
    secgrp_id = secgrp['GroupId']
    print('Deleting security group ' + secgrp_id)
    ec2_client.delete_security_group(GroupId=secgrp_id)

response = ec2_client.describe_images(Filters=filter)
for image in response['Images']:
    image_id = image['ImageId']
    print('Deleting image ' + image_id)
    ec2_client.deregister_image(ImageId=image_id)

response = ec2_client.describe_snapshots(Filters=filter)
for snapshot in response['Snapshots']:
    snapshot_id = snapshot['SnapshotId']
    print('Deleting snapshot ' + snapshot_id)
    ec2_client.delete_snapshot(SnapshotId=snapshot_id)

response = ec2_client.describe_addresses(Filters=filter)
for address in response['Addresses']:
    allocation_id = address['AllocationId']
    print('Deleting elastic ip ' + allocation_id)
    ec2_client.release_address(AllocationId=allocation_id)

print('Deleting ovimport bucket')
bucket = s3_resource.Bucket('osvimport')
bucket.objects.all().delete()
bucket.delete()

print('Deleting linuxbackend bucket')
bucket = s3_resource.Bucket('linuxbackend')
bucket.objects.all().delete()
bucket.delete()

print('Deleting controlbackend bucket')
bucket = s3_resource.Bucket('controlbackend')
bucket.objects.all().delete()
bucket.delete()

iam_client.delete_role_policy(RoleName='vmimport', PolicyName='vmimport')
iam_client.delete_role(RoleName='vmimport')



