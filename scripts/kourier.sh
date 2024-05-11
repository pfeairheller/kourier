#!/bin/bash

source /opt/healthkeri/kourier/venv/bin/activate
kourier start --config-dir /opt/healthkeri/kourier/config --host "0.0.0.0" --boothost "127.0.0.1"