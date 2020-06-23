#!/bin/bash

cd /usr/src/backend
/root/bin/capstan package init --name "Dummy Backend" --title "Dummy Backend" --author "Steffen"
/root/bin/capstan runtime init --runtime native
/root/bin/capstan package compose DummyBackend --pull-missing

