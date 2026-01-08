#!/bin/bash
# Setup script for Stori MSME App deployment

set -e

echo "=========================================="
echo "Stori MSME App Deployment Setup"
echo "=========================================="

# Step 1: Rebuild Next.js app
echo ""
echo "Step 1: Rebuilding Next.js app with /stori base path..."
cd /home/ubuntu/stori-web
npm run build

# Step 2: Setup systemd service
echo ""
echo "Step 2: Setting up systemd service..."
sudo cp stori-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable stori-app
sudo systemctl start stori-app

# Step 3: Check service status
echo ""
echo "Step 3: Checking service status..."
sudo systemctl status stori-app --no-pager

# Step 4: Update Nginx
echo ""
echo "Step 4: Please add the location blocks from 'nginx-stori-location-blocks.conf'"
echo "        to your Nginx config at /etc/nginx/sites-available/your-site"
echo ""
echo "Then run:"
echo "  sudo nginx -t"
echo "  sudo systemctl restart nginx"

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Access your app at: https://mycfo.club/stori"
echo "API health check: https://mycfo.club/stori/api/health"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u stori-app -f"
echo ""

