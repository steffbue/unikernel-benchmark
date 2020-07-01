#!/bin/bash

python3 prepare-control-server-ip.py
./compile-osv-backend.sh
./create-vmimport-role.sh
python3 prepare-resources.py