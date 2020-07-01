#!/bin/bash

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
nvm install -y node

cd /home/ec2-user
npm install

cd /etc/systemd/system
systemd enable nodeservice.service
systemd start nodeservice.service
