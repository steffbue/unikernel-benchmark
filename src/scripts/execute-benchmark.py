import threading
import requests
import time
import datetime
import random
import os
import boto3
import boto3.session
from botocore.exceptions import ClientError

BENCHMARK_NUMBER_ITERATIONS = 15


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
    for i in range(BENCHMARK_NUMBER_ITERATIONS):
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
            f.write(entry + '\n')
        f.close()

def measure_execution_time(ec2_client, ec2_resource, instance_id):
    instance = ec2_resource.Instance(instance_id)

    instance.start()
    instance.wait_until_running()

    time.sleep(30)

    results = []
    for i in range(BENCHMARK_NUMBER_ITERATIONS):
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

def measure_cpu_utilization(ec2_client, ec2_resource, cw_client, instance_id):
    instance = ec2_resource.Instance(instance_id)

    instance.start()
    instance.wait_until_running()

    start_time = datetime.datetime.utcnow().replace(microsecond=0, second=0)
    end_time = datetime.timedelta(minutes=10) + start_time
    time.sleep(600)

    response = cw_client.get_metric_statistics(Namespace='AWS/EC2', MetricName='CPUUtilization', Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}], StartTime=start_time, EndTime=end_time, Period=60, Statistics=['Average', 'Minimum', 'Maximum'])
    print(response)

    instance.stop()
    instance.wait_until_stopped()


def benchmark_linux(ec2_client, ec2_resource, cw_client):
    results_path = '/usr/src/results'
    linux_instance_id, control_linux_instance_id = retrieve_linux_instances_ids(ec2_client, ec2_resource)
    results_boot_time = measure_boot_time(ec2_client, ec2_resource, linux_instance_id, control_linux_instance_id)
    store_results(os.path.join(results_path, 'linux-boot-times.txt'), results_boot_time)
    time.sleep(30)
    results_execution_time = measure_execution_time(ec2_client, ec2_resource, linux_instance_id)
    store_results(os.path.join(results_path, 'linux-execution-times.txt'), results_execution_time)
    time.sleep(30)
    measure_cpu_utilization(ec2_client, ec2_resource, cw_client, linux_instance_id)

    return

def benchmark_osv(ec2_client, ec2_resource, cw_client):
    results_path = '/usr/src/results'
    osv_instance_id, control_osv_instance_id = retrieve_osv_instances_ids(ec2_client, ec2_resource)
    results_boot_time = measure_boot_time(ec2_client, ec2_resource, osv_instance_id, control_osv_instance_id)
    store_results(os.path.join(results_path, 'osv-boot-times.txt'), results_boot_time)
    time.sleep(30)
    results_execution_time = measure_execution_time(ec2_client, ec2_resource, osv_instance_id)  
    store_results(os.path.join(results_path, 'osv-execution-times.txt'), results_execution_time)
    time.sleep(30)
    measure_cpu_utilization(ec2_client, ec2_resource, cw_client, osv_instance_id)

    return




ec2_client_t1 = boto3.session.Session().client('ec2')
ec2_client_t2 = boto3.session.Session().client('ec2')
ec2_resource_t1 = boto3.session.Session().resource('ec2')
ec2_resource_t2 = boto3.session.Session().resource('ec2')
cw_client_t1 = boto3.session.Session().client('cloudwatch')
cw_client_t2 = boto3.session.Session().client('cloudwatch')

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



