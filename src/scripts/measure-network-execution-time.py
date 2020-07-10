import threading
import requests
import time
import datetime
import random
import os
import boto3
import boto3.session
from botocore.exceptions import ClientError
import measurehelper as mh

NUMBER_ITERATIONS = 15


def measure_network_execution_time(ec2_client, ec2_resource, s3_client, s3_resource, instance_id, bucket_name):
    instance = ec2_resource.Instance(instance_id)

    instance.start()
    instance.wait_until_running()

    time.sleep(30)

    s3_client.create_bucket(Bucket=bucket_name)
    bucket = s3_resource.Bucket(bucket_name)
    
    put_url = s3_client.generate_presigned_url('put_object', Params={'Bucket':bucket_name, 'Key':'randomNumbers.txt'})
    get_url = s3_client.generate_presigned_url('get_object', Params={'Bucket':bucket_name, 'Key':'randomNumbers.txt'})

    results = []
    for i in range(NUMBER_ITERATIONS):
        while(True):
            res = requests.put(
                'http://{}:8080/metric/network/execution'.format(instance.public_ip_address), json={'putURL': put_url, 'getURL': get_url})
            if res.status_code == 200:
                print(res.json())
                results.append(res.json()['ExecutionTime'])
                break
            else:
                sleep_time = int(random.uniform(5, 20))
                time.sleep(sleep_time)

    instance.stop()
    instance.wait_until_stopped()

    bucket.objects.all().delete()
    bucket.delete()

    print(results)

    return results


ec2_client_t1 = boto3.session.Session().client('ec2')
ec2_client_t2 = boto3.session.Session().client('ec2')
ec2_resource_t1 = boto3.session.Session().resource('ec2')
ec2_resource_t2 = boto3.session.Session().resource('ec2')
s3_client_t1 = boto3.session.Session().client('s3', endpoint_url='https://s3.eu-central-1.amazonaws.com')
s3_client_t2 = boto3.session.Session().client('s3', endpoint_url='https://s3.eu-central-1.amazonaws.com')

def benchmark_linux(ec2_client, ec2_resource, s3_client):
    results_path = '/usr/src/results'
    linux_instance_id, control_linux_instance_id = mh.retrieve_linux_instances_ids(ec2_client, ec2_resource)
    results_execution_time = measure_network_execution_time(ec2_client, ec2_resource, s3_client, linux_instance_id, 'linuxbenchmark')
    mh.store_results(os.path.join(results_path, 'linux-network-execution-times.txt'), results_execution_time)
    return


def benchmark_osv(ec2_client, ec2_resource, s3_client):
    results_path = '/usr/src/results'
    osv_instance_id, control_osv_instance_id = mh.retrieve_osv_instances_ids(ec2_client, ec2_resource)
    results_execution_time = measure_network_execution_time(ec2_client, ec2_resource, s3_client, osv_instance_id, 'osvbenchmark')
    mh.store_results(os.path.join(results_path, 'osv-network-execution-times.txt'), results_execution_time)
    return


try:
    t1 = threading.Thread(target=benchmark_linux,args=(ec2_client_t1, ec2_resource_t1, s3_client_t1))
    t2 = threading.Thread(target=benchmark_osv, args=(ec2_client_t2, ec2_resource_t2, s3_client_t2))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


except ClientError as e:
    print(e)
    exit(1)
