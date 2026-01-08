# Stori AI Favicon Setup Guide

## ✅ Created Files

All favicon files have been created in the `public/` folder:

- ✨ **favicon.svg** - Main favicon (512x512, high quality with gradient)
- 📱 **favicon-32x32.svg** - Small size for browser tabs
- 🍎 **apple-touch-icon.svg** - For iOS devices (180x180)
- 📲 **icon-192.png.svg** - For Android devices (192x192)
- 📄 **manifest.json** - PWA manifest for installable app

## 🎨 Design Features

- **Purple-Pink Gradient**: #667eea → #764ba2 → #f093fb
- **Modern "S" Letter**: Bold, professional design
- **AI Sparkles**: Small decorative elements suggesting AI technology
- **White Letter**: High contrast for visibility

## 🚀 Deploy Instructions

### On Server:

```bash
cd /home/ubuntu/stori-web

# Create favicon.ico from SVG (you need to do this manually)
# Option 1: Use online converter (recommended)
# - Go to: https://cloudconvert.com/svg-to-ico
# - Upload: public/favicon-32x32.svg
# - Download as: favicon.ico
# - Upload to: public/favicon.ico

# Option 2: Use ImageMagick (if installed)
sudo apt-get install imagemagick
convert public/favicon-32x32.svg public/favicon.ico

# Rebuild and restart
npm run build
sudo systemctl restart stori-app
```

## 📋 What's Configured

### In `app/layout.tsx`:
- ✅ Multiple favicon sizes for all devices
- ✅ Apple touch icon for iOS
- ✅ PWA manifest for installable app
- ✅ Theme color matching brand (#667eea)
- ✅ Proper metadataBase for `/stori` basePath

### Browser Support:
- ✅ Modern browsers: Use **favicon.svg** (scalable, crisp)
- ✅ Older browsers: Use **favicon.ico** (fallback)
- ✅ iOS Safari: Use **apple-touch-icon.svg**
- ✅ Android Chrome: Use **icon-192.png.svg**

## 🔍 Testing

After deployment, test on:

1. **Desktop Browsers:**
   - Chrome: Check tab icon
   - Firefox: Check tab icon
   - Safari: Check tab icon
   - Edge: Check tab icon

2. **Mobile Devices:**
   - iOS: Add to Home Screen → Should show Stori logo
   - Android: Add to Home Screen → Should show Stori logo

3. **URLs to Test:**
   - https://mycfo.club/stori
   - https://mycfo.club/stori/msmes
   - https://mycfo.club/stori/msmes/msme-1

## 🎯 Expected Result

- ✅ All pages show **Stori "S" logo** with purple gradient
- ✅ Favicon persists across navigation
- ✅ Different from MyCFO root favicon
- ✅ High quality on all screen sizes (thanks to SVG)

## 🛠️ Convert SVG to ICO (Required)

Since browsers still need ICO format for older support, convert the SVG:

### Online Converter (Easiest):
1. Go to: https://cloudconvert.com/svg-to-ico
2. Upload: `public/favicon-32x32.svg`
3. Convert to ICO (32x32)
4. Download
5. Upload to server: `public/favicon.ico`

### Or use this tool:
- https://favicon.io/favicon-converter/
- Upload the `favicon.svg` file
- Download the generated `favicon.ico`

## 📱 PWA Support

The app can now be installed as a PWA:
- Theme color: Purple (#667eea)
- App name: "Stori AI"
- Works offline with proper service worker setup

---

**Created:** $(date)
**Version:** 1.0

