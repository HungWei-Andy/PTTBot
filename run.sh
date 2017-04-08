#!/bin/bash
if [ ! -d "./nlu/models" ]; then
    bash download.sh
fi

python test.py
