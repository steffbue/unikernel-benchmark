#!/bin/bash

python3 create-control-server-ip.py
./compile-osv-backend.sh
./upload-files.sh
./create-roles.sh
./import-snapshot.sh