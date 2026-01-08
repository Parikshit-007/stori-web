#!/bin/bash
# Fix Stori Next.js App - Diagnostic and Fix Script

echo "=========================================="
echo "Stori App Diagnostic & Fix"
echo "=========================================="

# Check 1: Is Next.js app running?
echo ""
echo "1. Checking if Next.js app is running..."
if sudo systemctl is-active --quiet stori-app; then
    echo "   ✓ Service is running"
    sudo systemctl status stori-app --no-pager | head -5
else
    echo "   ✗ Service is NOT running"
    echo "   Starting service..."
    sudo systemctl start stori-app
    sleep 2
    sudo systemctl status stori-app --no-pager | head -5
fi

# Check 2: Is port 3000 listening?
echo ""
echo "2. Checking port 3000..."
if sudo netstat -tlnp | grep -q ":3000 "; then
    echo "   ✓ Port 3000 is in use"
    sudo netstat -tlnp | grep ":3000 "
else
    echo "   ✗ Port 3000 is NOT in use"
    echo "   App is not listening on port 3000"
fi

# Check 3: Test local connection
echo ""
echo "3. Testing local connection to app..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/stori 2>/dev/null)
if [ "$response" = "200" ] || [ "$response" = "404" ]; then
    echo "   ✓ App is responding (HTTP $response)"
    echo "   Testing full response..."
    curl -s http://localhost:3000/stori | head -10
else
    echo "   ✗ App is NOT responding (HTTP $response)"
fi

# Check 4: Check if app is built
echo ""
echo "4. Checking if app is built..."
if [ -d "/home/ubuntu/stori-web/.next" ]; then
    echo "   ✓ .next directory exists"
    ls -la /home/ubuntu/stori-web/.next | head -5
else
    echo "   ✗ .next directory NOT found"
    echo "   Need to build the app!"
fi

# Check 5: View recent logs
echo ""
echo "5. Recent app logs:"
sudo journalctl -u stori-app -n 30 --no-pager | tail -20

echo ""
echo "=========================================="
echo "Diagnostic Complete"
echo "=========================================="

