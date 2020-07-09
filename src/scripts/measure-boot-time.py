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

def measure_boot_time(ec2_client, ec2_resource, instance_id, control_instance_id):
    control_instance = ec2_resource.Instance(control_instance_id)
    instance = ec2_resource.Instance(instance_id)

    control_instance.wait_until_stopped()
    instance.wait_until_stopped()

    control_instance.start()
    control_instance.wait_until_running()

    time.sleep(30)


    results = []
    for i in range(NUMBER_ITERATIONS):
        instance.wait_until_stopped()
        while(True):
            res_start = requests.put('http://{}:8080/metric/boot/start'.format(control_instance.public_ip_address))
            if res_start.status_code == 200:
                break
            else:
                sleep_time = int(random.uniform(5,20))
                time.sleep(sleep_time)
        while(True):
            res_result = requests.get('http://{}:8080/metric/boot/result'.format(control_instance.public_ip_address))
            if res_result.status_code == 200:
                print(res_result.json())
                results.append(res_result.json()['BootTime'])
                break
            else:
                sleep_time = int(random.uniform(5,20))
                time.sleep(sleep_time)

    control_instance.stop()
    control_instance.wait_until_stopped()

    print(results)

    return results

ec2_client_t1 = boto3.session.Session().client('ec2')
ec2_client_t2 = boto3.session.Session().client('ec2')
ec2_resource_t1 = boto3.session.Session().resource('ec2')
ec2_resource_t2 = boto3.session.Session().resource('ec2')

def benchmark_linux(ec2_client, ec2_resource):
    linux_instance_id, control_linux_instance_id = mh.retrieve_linux_instances_ids(ec2_client, ec2_resource)
    results_boot_time = measure_boot_time(ec2_client, ec2_resource, linux_instance_id, control_linux_instance_id)
    results_path = '/usr/src/results'
    mh.store_results(os.path.join(results_path, 'linux-boot-times.txt'), results_boot_time)
    return

def benchmark_osv(ec2_client, ec2_resource):
    osv_instance_id, control_osv_instance_id = mh.retrieve_osv_instances_ids(ec2_client, ec2_resource)
    results_boot_time = measure_boot_time(ec2_client, ec2_resource, osv_instance_id, control_osv_instance_id)
    results_path = '/usr/src/results'
    mh.store_results(os.path.join(results_path, 'osv-boot-times.txt'), results_boot_time)
    return
try:
    t1 = threading.Thread(target=benchmark_linux, args=(ec2_client_t1, ec2_resource_t1))
    t2 = threading.Thread(target=benchmark_osv, args=(ec2_client_t2, ec2_resource_t2))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


except ClientError as e:
    print(e)
    exit(1)