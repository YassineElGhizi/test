#!/bin/bash

source /root/test/venv/bin/activate
export PYTHONPATH=$PYTHONPATH:/root/test
python3 /root/test/web_scrappers/bbc.py