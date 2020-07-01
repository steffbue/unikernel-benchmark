#!/bin/bash

scp -r -i benchmark-key.pem /usr/src/backend_linux ec2-user@$1:/home/ec2-user/
scp -i benchmark-key.pem /usr/src/aws/config/nodeserver.service ec2-user@$1:/etc/systemd/system/nodeserver.service
echo 'cd /home/ec2-user/; ./startup.sh' | ssh -o 'StrictHostKeyChecking no' -o 'ConnectionAttempts 30' -i benchmark-key.pem ec2-user@$1 /bin/bash