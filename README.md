# Unikernel Benchmark

## Requirements

- Linux machine with Docker installed
- AWS User having:
    - terminal and console access
    - full access on EC2, S3 and IAM

## Preparation Part 1

Clone the repository and execute the following commands to prepare the benchmark:

```bash
cd unikernel-benchmark/scripts
export AWS_ACCESS_KEY_ID=<Your-Access-Key>
export AWS_SECRET_ACCESS_KEY=<Your-Secret-Access-Key>
export AWS_DEFAULT_REGION=eu-central-1
./prepare-benchmark-part-one.sh
```
## Manual steps

Login into the AWS console and go to the EC2 service. Expand the "Elastic Block Store" menu entry and select "Snapshots". You should now see a snapshot with the description "Created by AWS-VMImport service". If not, wait a while and refresh the page until the snapshot is created. Right-click on the snapshot and select "Create Image". Enter "OSv image" as name and make sure that Architecture is "x86_64" and Virtualization type is "Hardware-assisted virtualization" and click "Create" to create the image. Right-click on the snapshot, select "Add/Edit Tags" and create a tag with the key "Benchmark" and value "Unikernel". Go to "AMIs" and repeat the tag creation process for the image.

## Preparation Part 2

Execute the following command to prepare the EC2 instances for the benchmark:

```bash
./prepare-benchmark-part-two.sh
```
Four instances with the tag Key=Benchmark, Value=Unikernel will be created. You can see them by clicking on the "Instances" entry. Wait until each of these instances have switched to the stopping state before continuing with the Execution Part. 
(Make sure to use the same terminal as in Part 1. If not, re-execute the export commands)

## Execution Part

You can measure the four metrics (Boot Time, Stop Time, Execution Time (Network-I/O), Execution Time (Network-I/O)) by executing the respective measure script:

### Boot Time and Stop Time 

```bash
./measure-boot-stop-time.sh
```

### Execution Time (Network-I/O)

```bash
./measure-network-execution-time.sh
```

### Execution Time (Disk-I/O)

```bash
./measure-disk-execution-time.sh
```

After measuring every metric, you can create plots for them by executing ./create-plots.sh. The plots can be found in unikernel-benchmark/src/results.
(Make sure to not execute more than one execution script at the same time)

## Benchmark Cleanup

Execute the following script to delete allocated resources:

```bash
./clean-benchmark.sh
```








