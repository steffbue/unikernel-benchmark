#!/bin/bash

curl --silent --location https://rpm.nodesource.com/setup_14.x | sudo bash -
yum -y install nodejs

cd /backend_linux
npm install

echo "@reboot node /backend_linux/server.js &" >> /var/spool/cron/ec2-user
