# Troubleshooting 404 on /stori

## Quick Checks

1. **Is Next.js app running?**
```bash
sudo systemctl status stori-app
```

2. **Is it listening on port 3000?**
```bash
sudo netstat -tlnp | grep 3000
# OR
curl http://localhost:3000/stori
```

3. **Check Next.js logs**
```bash
sudo journalctl -u stori-app -n 50 --no-pager
```

4. **Test backend API**
```bash
curl http://localhost:8002/api/health
```

## Common Issues

### Issue 1: Next.js app not running
**Solution:**
```bash
cd /home/ubuntu/stori-web
sudo systemctl start stori-app
sudo systemctl status stori-app
```

### Issue 2: App not built with basePath
**Solution:**
```bash
cd /home/ubuntu/stori-web
npm run build
sudo systemctl restart stori-app
```

### Issue 3: Port conflict
**Solution:**
```bash
# Check what's using port 3000
sudo lsof -i :3000
# Kill if needed
sudo kill -9 <PID>
sudo systemctl restart stori-app
```

### Issue 4: Next.js not starting correctly
**Solution:**
```bash
# Test manually
cd /home/ubuntu/stori-web
npm start
# If this works, the issue is with systemd service
```

