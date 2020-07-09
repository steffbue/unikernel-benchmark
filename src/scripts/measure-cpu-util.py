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

def measure_cpu_utilization(ec2_client, ec2_resource, cw_client, instance_id):
    instance = ec2_resource.Instance(instance_id)

    instance.start()
    instance.wait_until_running()

    start_time = datetime.datetime.utcnow().replace(microsecond=0, second=0)
    end_time = datetime.timedelta(minutes=15) + start_time
    instance.monitor()
    time.sleep(900)

    response = cw_client.get_metric_statistics(Namespace='AWS/EC2', MetricName='CPUUtilization', Dimensions=[
                                               {'Name': 'InstanceId', 'Value': instance_id}], StartTime=start_time, EndTime=end_time, Period=60, Statistics=['Average', 'Minimum', 'Maximum'])
    print(response)

    instance.stop()
    instance.wait_until_stopped()
    return


ec2_client_t1 = boto3.session.Session().client('ec2')
ec2_client_t2 = boto3.session.Session().client('ec2')
ec2_resource_t1 = boto3.session.Session().resource('ec2')
ec2_resource_t2 = boto3.session.Session().resource('ec2')
cw_client_t1 = boto3.session.Session().client('cloudwatch')
cw_client_t2 = boto3.session.Session().client('cloudwatch')


def benchmark_linux(ec2_client, ec2_resource, cw_client):
    results_path = '/usr/src/results'
    linux_instance_id, control_linux_instance_id = mh.retrieve_linux_instances_ids(ec2_client, ec2_resource)
    measure_cpu_utilization(ec2_client, ec2_resource, cw_client, linux_instance_id)

    return


def benchmark_osv(ec2_client, ec2_resource, cw_client):
    results_path = '/usr/src/results'
    osv_instance_id, control_osv_instance_id = mh.retrieve_osv_instances_ids(ec2_client, ec2_resource)
    measure_cpu_utilization(ec2_client, ec2_resource, cw_client, osv_instance_id)

    return


try:
    t1 = threading.Thread(target=benchmark_linux, args=(ec2_client_t1, ec2_resource_t1, cw_client_t1))
    t2 = threading.Thread(target=benchmark_osv, args=(ec2_client_t2, ec2_resource_t2, cw_client_t2))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


except ClientError as e:
    print(e)
    exit(1)
