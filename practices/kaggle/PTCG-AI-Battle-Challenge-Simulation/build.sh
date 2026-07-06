#!/bin/bash
set -e

cd "$(dirname "$0")/agent"
tar -czf ../submission.tar.gz main.py deck.csv utils.py cg/
echo "Created submission.tar.gz"
