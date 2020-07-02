#!/bin/bash

curl --silent --location https://rpm.nodesource.com/setup_14.x | sudo bash -
yum -y install nodejs

cd /backend
npm install

echo "@reboot /backend/run.sh" >> /var/spool/cron/ec2-user
