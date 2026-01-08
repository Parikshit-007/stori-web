#!/bin/bash
# Check Stori App Logs

echo "=== Recent Error Logs ==="
sudo journalctl -u stori-app -n 50 --no-pager

echo ""
echo "=== Checking Node.js and npm ==="
which node
which npm
node --version
npm --version

echo ""
echo "=== Testing manual start ==="
cd /home/ubuntu/stori-web
pwd
ls -la package.json

