#!/bin/bash

curl --silent --location https://rpm.nodesource.com/setup_14.x | sudo bash -
yum -y install nodejs

npm install

echo "@reboot node /server.js" >> /var/spool/cron/ec2-user
