#!/bin/bash
# Fix 502 Bad Gateway - Next.js App Not Responding

echo "=========================================="
echo "Fixing 502 Bad Gateway Error"
echo "=========================================="

# Step 1: Check if port 3000 is listening
echo ""
echo "1. Checking port 3000..."
if sudo netstat -tlnp | grep -q ":3000 "; then
    echo "   ✓ Port 3000 is in use"
    sudo netstat -tlnp | grep ":3000 "
    PID=$(sudo lsof -t -i:3000)
    echo "   Process PID: $PID"
    ps aux | grep $PID | grep -v grep
else
    echo "   ✗ Port 3000 is NOT in use"
    echo "   Next.js app is not running!"
fi

# Step 2: Check service status
echo ""
echo "2. Checking stori-app service..."
sudo systemctl status stori-app --no-pager | head -15

# Step 3: Check recent errors
echo ""
echo "3. Recent error logs:"
sudo journalctl -u stori-app -n 20 --no-pager | tail -15

# Step 4: Stop service and clear port
echo ""
echo "4. Stopping service and clearing port 3000..."
sudo systemctl stop stori-app
sleep 2

# Kill any process on port 3000
if sudo lsof -t -i:3000 > /dev/null 2>&1; then
    echo "   Killing process on port 3000..."
    sudo fuser -k 3000/tcp
    sleep 2
fi

# Step 5: Verify app is built
echo ""
echo "5. Checking if app is built..."
cd /home/ubuntu/stori-web
if [ -d ".next" ]; then
    echo "   ✓ .next directory exists"
    ls -la .next | head -3
else
    echo "   ✗ .next directory NOT found"
    echo "   Building app..."
    npm run build
fi

# Step 6: Test manual start
echo ""
echo "6. Testing manual start (5 seconds)..."
timeout 5 npm start 2>&1 &
MANUAL_PID=$!
sleep 3
if ps -p $MANUAL_PID > /dev/null; then
    echo "   ✓ Manual start works!"
    kill $MANUAL_PID 2>/dev/null
else
    echo "   ✗ Manual start failed"
fi

# Step 7: Restart service
echo ""
echo "7. Restarting service..."
sudo systemctl start stori-app
sleep 3
sudo systemctl status stori-app --no-pager | head -10

# Step 8: Test connection
echo ""
echo "8. Testing local connection..."
sleep 2
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/stori 2>/dev/null)
if [ "$response" = "200" ] || [ "$response" = "404" ]; then
    echo "   ✓ App is responding (HTTP $response)"
else
    echo "   ✗ App is NOT responding (HTTP $response)"
fi

echo ""
echo "=========================================="
echo "Diagnostic Complete"
echo "=========================================="

