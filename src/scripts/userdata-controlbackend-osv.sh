#!/bin/bash

aws s3 cp s3://controlbackend/osv.tar.gz osv.tar.gz
tar -xf osv.tar.gz --strip-components 1
chmod +x config.sh
./config.sh