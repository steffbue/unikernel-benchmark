import threading
import requests
import time
import random
import os
import boto3
import boto3.session
from botocore.exceptions import ClientError

import statistics as st
import matplotlib.pyplot as plt


def retrieve_linux_instances_ids(ec2_client, ec2_resource):
    filterBenchmark = {'Name': 'tag:Benchmark', 'Values': ['Unikernel']}
    filterLinuxInstance = {'Name': 'tag:Type', 'Values': ['Linux']}
    filterControlLinuxInstance = {'Name': 'tag:Type', 'Values': ['Control-Linux']}
    filterStoppedInstance = {'Name': 'instance-state-name', 'Values': ['stopped']}

    resp_describe = ec2_client.describe_instances(Filters=[filterBenchmark, filterLinuxInstance, filterStoppedInstance])
    linux_instance_id = resp_describe['Reservations'][0]['Instances'][0]['InstanceId']

    resp_describe = ec2_client.describe_instances(Filters=[filterBenchmark, filterControlLinuxInstance, filterStoppedInstance])
    control_linux_instance_id = resp_describe['Reservations'][0]['Instances'][0]['InstanceId']

    return linux_instance_id, control_linux_instance_id

def retrieve_osv_instances_ids(ec2_client, ec2_resource):
    filterBenchmark = {'Name': 'tag:Benchmark', 'Values': ['Unikernel']}
    filterLinuxInstance = {'Name': 'tag:Type', 'Values': ['OSV']}
    filterControlLinuxInstance = {'Name': 'tag:Type', 'Values': ['Control-OSV']}
    filterStoppedInstance = {'Name': 'instance-state-name', 'Values': ['stopped']}

    resp_describe = ec2_client.describe_instances(Filters=[filterBenchmark, filterLinuxInstance, filterStoppedInstance])
    osv_instance_id = resp_describe['Reservations'][0]['Instances'][0]['InstanceId']

    resp_describe = ec2_client.describe_instances(Filters=[filterBenchmark, filterControlLinuxInstance, filterStoppedInstance])
    control_osv_instance_id = resp_describe['Reservations'][0]['Instances'][0]['InstanceId']

    return osv_instance_id, control_osv_instance_id

def measure_boot_time(ec2_client, ec2_resource, instance_id, control_instance_id):
    control_instance = ec2_resource.Instance(control_instance_id)
    instance = ec2_resource.Instance(instance_id)

    control_instance.wait_until_stopped()
    instance.wait_until_stopped()

    control_instance.start()
    control_instance.wait_until_running()

    time.sleep(30)


    results = []
    for i in range(20):
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

def store_results(path, results):
    with open(path, 'w') as f:
        for entry in results:
            f.write(entry)
        f.close()

def measure_execution_time(ec2_client, ec2_resource, instance_id):
    instance = ec2_resource.Instance(instance_id)

    instance.wait_until_stopped()
    instance.start()
    instance.wait_until_running()

    time.sleep(30)

    results = []
    for i in range(20):
        while(True):
            res = requests.get('http://{}:8080/metric/execution'.format(instance.public_ip_address))
            if res.status_code == 200:
                print(res.json())
                results.append(res.json()['ExecutionTime'])
                break
            else:
                sleep_time = int(random.uniform(5,20))
                time.sleep(sleep_time)
            
    
    instance.stop()
    instance.wait_until_stopped()

    print(results)

    return results

def benchmark_linux(ec2_client, ec2_resource):
    linux_instance_id, control_linux_instance_id = retrieve_linux_instances_ids(ec2_client, ec2_resource)
    results_boot_time = measure_boot_time(ec2_client, ec2_resource, linux_instance_id, control_linux_instance_id, results_boot_time)
    results_execution_time = measure_execution_time(ec2_client, ec2_resource, linux_instance_id, results_execution_time)

    results_path = '/usr/src/results'
    store_results(os.path.join(results_path, 'linux-boot-times.txt'), results_boot_time)
    store_results(os.path.join(results_path, 'linux-execution-times.txt'), results_execution_time)

    return

def benchmark_osv(ec2_client, ec2_resource):
    osv_instance_id, control_osv_instance_id = retrieve_osv_instances_ids(ec2_client, ec2_resource)
    results_boot_time = measure_boot_time(ec2_client, ec2_resource, osv_instance_id, control_osv_instance_id, results_boot_time)
    results_execution_time = measure_execution_time(ec2_client, ec2_resource, osv_instance_id, results_execution_time)  

    results_path = '/usr/src/results'
    store_results(os.path.join(results_path, 'osv-boot-times.txt'), results_boot_time)
    store_results(os.path.join(results_path, 'osv-execution-times.txt'), results_execution_time)

    return




ec2_client_t1 = boto3.session.Session().client('ec2')
ec2_client_t2 = boto3.session.Session().client('ec2')
ec2_resource_t1 = boto3.session.Session().resource('ec2')
ec2_resource_t2 = boto3.session.Session().resource('ec2')

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



