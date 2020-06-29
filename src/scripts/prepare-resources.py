import boto3
from botocore.exceptions import ClientError

iam_client = boto3.client('iam')
tag = {'Key': 'Benchmark', 'Value': 'Unikernel'}
tag_specification_snapshot = {'ResourceType': 'snapshot', 'Tags': [tag]}


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
    return

def upload_osvimage_s3(s3_client):
    os.chdir('/root/.capstan/instances/qemu/DummyBackend')

    s3_client.create_bucket(Bucket='osvimport')
    bucket = s3.Bucket('osvimport')
    bucket.upload_file('disk.vhd', 'disk.vhd')
    return

def import_osvimage_snapshot(ec2_client):
    os.chdir('/usr/src/aws/config')

    with open('container.json', 'r') as container_file:
        container_json = json.load(container_file)
        ec2_client.import_snapshot(Description='OSv Image', DiskContainer=container_json, TagSpecifications=[tag_specification_snapshot])
        container_file.close()
    return


try:
    upload_osvimage_s3(ec2_client)
    create_vmimport_policy(iam_client)
    import_osvimage_snapshot(ec2_client)
    
except ClientError as e:
    print(e)
    exit(1)