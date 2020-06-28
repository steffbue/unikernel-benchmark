#!/bin/bash

IP_ADDRESS=$1

scp -i keypair.pem /usr/src/backend_linux $IP_ADDRESS:/
ssh -i keypair.pem $IP_ADDRESS