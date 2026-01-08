#!/bin/bash
# Update Stori App to use Port 3001

echo "=========================================="
echo "Updating Stori App to Port 3001"
echo "=========================================="

# Step 1: Stop service
echo ""
echo "1. Stopping stori-app service..."
sudo systemctl stop stori-app

# Step 2: Update package.json
echo ""
echo "2. Updating package.json..."
cd /home/ubuntu/stori-web
sed -i 's/"start": "next start -p 3000"/"start": "next start -p 3001"/' package.json
echo "   ✓ package.json updated"

# Step 3: Update systemd service
echo ""
echo "3. Updating systemd service..."
sudo sed -i 's/Environment="PORT=3000"/Environment="PORT=3001"/' /etc/systemd/system/stori-app.service
sudo systemctl daemon-reload
echo "   ✓ systemd service updated"

# Step 4: Update Nginx config
echo ""
echo "4. Updating Nginx config..."
sudo sed -i 's|proxy_pass http://127.0.0.1:3000;|proxy_pass http://127.0.0.1:3001;|' /etc/nginx/sites-available/mycfo
sudo nginx -t
if [ $? -eq 0 ]; then
    echo "   ✓ Nginx config updated and validated"
    sudo systemctl restart nginx
else
    echo "   ✗ Nginx config has errors!"
fi

# Step 5: Start service
echo ""
echo "5. Starting stori-app service..."
sudo systemctl start stori-app
sleep 3
sudo systemctl status stori-app --no-pager | head -10

# Step 6: Test
echo ""
echo "6. Testing connection..."
sleep 2
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/stori 2>/dev/null)
if [ "$response" = "200" ] || [ "$response" = "404" ]; then
    echo "   ✓ App is responding on port 3001 (HTTP $response)"
else
    echo "   ✗ App is NOT responding (HTTP $response)"
fi

echo ""
echo "=========================================="
echo "Update Complete!"
echo "=========================================="
echo ""
echo "Access your app at: https://mycfo.club/stori"
echo ""

