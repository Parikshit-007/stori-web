#!/bin/bash
# Fix Port 3000 Conflict

echo "=========================================="
echo "Fixing Port 3000 Conflict"
echo "=========================================="

# Step 1: Find what's using port 3000
echo ""
echo "1. Finding process using port 3000..."
PID=$(sudo lsof -t -i:3000)
if [ -z "$PID" ]; then
    echo "   No process found (might be using netstat method)"
    sudo netstat -tlnp | grep :3000
else
    echo "   Found process: PID $PID"
    ps aux | grep $PID | grep -v grep
fi

# Step 2: Stop the service first
echo ""
echo "2. Stopping stori-app service..."
sudo systemctl stop stori-app

# Step 3: Kill any process on port 3000
echo ""
echo "3. Killing process on port 3000..."
if [ ! -z "$PID" ]; then
    echo "   Killing PID $PID"
    sudo kill -9 $PID
    sleep 2
else
    # Try netstat method
    sudo netstat -tlnp | grep :3000 | awk '{print $7}' | cut -d'/' -f1 | xargs -r sudo kill -9
fi

# Step 4: Verify port is free
echo ""
echo "4. Verifying port 3000 is free..."
if sudo lsof -t -i:3000 > /dev/null 2>&1; then
    echo "   ⚠ Port 3000 still in use, trying harder..."
    sudo fuser -k 3000/tcp
    sleep 2
else
    echo "   ✓ Port 3000 is now free"
fi

# Step 5: Start service
echo ""
echo "5. Starting stori-app service..."
sudo systemctl start stori-app
sleep 3

# Step 6: Check status
echo ""
echo "6. Service status:"
sudo systemctl status stori-app --no-pager | head -10

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="

