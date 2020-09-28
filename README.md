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

Login into the AWS console and go to the EC2 service. Expand the "Elastic Block Store" menu entry and select "Snapshots". You should now see a snapshot with the description "Created by AWS-VMImport service". If not, wait a while and refresh the page until the snapshot is created. Right-click on the snapshot and select "Create Image". Enter "OSv image" as name and make sure that Architecture is "x86_64" and Virtualization type is "Hardware-assisted virtualization". Click "Create" to create the image. Right-click on the snapshot, select "Add/Edit Tags" and create a tag with the key "Benchmark" and value "Unikernel".



