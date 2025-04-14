#!/bin/bash

if ! command -v perl &> /dev/null; then
    sudo apt update
    sudo apt install -y perl
fi

perl -MLWP::UserAgent -e1 2>/dev/null
if [ $? -ne 0 ]; then
    sudo apt install -y cpanminus || sudo apt install -y liblwp-useragent-determined-perl
    sudo cpanm LWP::UserAgent
fi
