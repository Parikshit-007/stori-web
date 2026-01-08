# Stori MSME App Deployment Instructions

## Step 1: Rebuild Next.js App with Base Path

```bash
cd /home/ubuntu/stori-web
npm run build
```

This will create the build in `.next` folder with `/stori` base path.

## Step 2: Update Nginx Configuration

Add this to your existing Nginx config at `/etc/nginx/sites-available/your-site`:

```nginx
# Add inside your existing server block (after the MyCFO location blocks)

# Stori MSME App - /stori path
location /stori {
    # Proxy to Next.js server (we'll run it on port 3000)
    proxy_pass http://127.0.0.1:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
    
    # Timeout settings
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}

# API proxy - Backend MSME Credit Scoring API
location /stori/api/ {
    proxy_pass http://127.0.0.1:8002/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # CORS headers
    add_header Access-Control-Allow-Origin * always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    
    if ($request_method = OPTIONS) {
        return 204;
    }
}
```

## Step 3: Create Systemd Service for Next.js App

Create `/etc/systemd/system/stori-app.service`:

```ini
[Unit]
Description=Stori MSME Next.js App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/stori-web
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**OR use PM2 (Recommended):**

```bash
# Install PM2
sudo npm install -g pm2

# Start app with PM2
cd /home/ubuntu/stori-web
pm2 start npm --name "stori-app" -- start
pm2 save
pm2 startup
```

## Step 4: Update package.json Scripts

Make sure your `package.json` has:

```json
{
  "scripts": {
    "start": "next start -p 3000"
  }
}
```

## Step 5: Restart Services

```bash
# Restart Nginx
sudo nginx -t
sudo systemctl restart nginx

# Start Next.js app (if using systemd)
sudo systemctl daemon-reload
sudo systemctl enable stori-app
sudo systemctl start stori-app

# OR if using PM2
pm2 restart stori-app
```

## Step 6: Test

- Frontend: `https://mycfo.club/stori`
- API: `https://mycfo.club/stori/api/health`
- API Docs: `https://mycfo.club/stori/api/docs`

## Alternative: Static Export (If no dynamic routes needed)

If you don't need server-side rendering, you can use static export:

1. Update `next.config.ts`:
```typescript
output: 'export',
```

2. Build:
```bash
npm run build
```

3. Serve static files:
```nginx
location /stori {
    alias /home/ubuntu/stori-web/out;
    try_files $uri $uri/ /stori/index.html;
}
```

