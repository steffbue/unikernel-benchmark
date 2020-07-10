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

NUMBER_ITERATIONS = 20


def measure_execution_time(ec2_client, ec2_resource, instance_id):
    instance = ec2_resource.Instance(instance_id)

    instance.start()
    instance.wait_until_running()

    time.sleep(30)

    results = []
    for i in range(NUMBER_ITERATIONS):
        while(True):
            res = requests.get(
                'http://{}:8080/metric/disk/execution'.format(instance.public_ip_address))
            if res.status_code == 200:
                print(res.json())
                results.append(res.json()['ExecutionTime'])
                break
            else:
                sleep_time = int(random.uniform(5, 20))
                time.sleep(sleep_time)

    instance.stop()
    instance.wait_until_stopped()

    print(results)

    return results


ec2_client_t1 = boto3.session.Session().client('ec2')
ec2_client_t2 = boto3.session.Session().client('ec2')
ec2_resource_t1 = boto3.session.Session().resource('ec2')
ec2_resource_t2 = boto3.session.Session().resource('ec2')

def benchmark_linux(ec2_client, ec2_resource):
    results_path = '/usr/src/results'
    linux_instance_id, control_linux_instance_id = mh.retrieve_linux_instances_ids(ec2_client, ec2_resource)
    results_execution_time = measure_execution_time(ec2_client, ec2_resource, linux_instance_id)
    mh.store_results(os.path.join(results_path, 'linux-disk-execution-times.txt'), results_execution_time)
    return


def benchmark_osv(ec2_client, ec2_resource):
    results_path = '/usr/src/results'
    osv_instance_id, control_osv_instance_id = mh.retrieve_osv_instances_ids(ec2_client, ec2_resource)
    results_execution_time = measure_execution_time(ec2_client, ec2_resource, osv_instance_id)
    mh.store_results(os.path.join(results_path, 'osv-disk-execution-times.txt'), results_execution_time)
    return


try:
    t1 = threading.Thread(target=benchmark_linux,args=(ec2_client_t1, ec2_resource_t1))
    t2 = threading.Thread(target=benchmark_osv, args=(ec2_client_t2, ec2_resource_t2))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


except ClientError as e:
    print(e)
    exit(1)
