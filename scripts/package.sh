#!/bin/bash

python setup.py sdist
tar czf kourier-install-0.0.1.tar.gz dist/kourier-0.0.1.tar.gz conf/kourier.conf scripts/kourier.sh
s3cmd put kourier-install-0.0.1.tar.gz s3://healthkeri-deployment/kourier/