# Quick Tesseract Installation Guide

## ✅ Method 1: Direct Download (Recommended - 2 minutes)

1. **Download the installer:**
   - Click this link: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.4.0.20240605.exe
   - Or visit: https://github.com/UB-Mannheim/tesseract/wiki

2. **Run the installer:**
   - Double-click the downloaded `.exe` file
   - **IMPORTANT:** During installation, check the box **"Add to PATH"**
   - Click "Install" and wait for completion

3. **Verify installation:**
   ```powershell
   tesseract --version
   ```
   Should show: `tesseract 5.4.0` (or similar)

4. **Restart your Django server:**
   - Stop server (Ctrl+C)
   - Start again: `python manage.py runserver`

## ✅ Method 2: Using Winget (if available)

```powershell
winget install --id UB-Mannheim.TesseractOCR
```

Then restart your server.

## ✅ Method 3: Using Chocolatey (if available)

```powershell
choco install tesseract
```

Then restart your server.

## ✅ Method 4: Manual Path (if already installed elsewhere)

If Tesseract is installed but not in PATH, set environment variable:

**Temporary (current session):**
```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**Permanent:**
1. Open System Properties → Environment Variables
2. Add new variable:
   - Name: `TESSERACT_CMD`
   - Value: `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. Restart terminal/server

## After Installation

Once Tesseract is installed, your OCR API will work automatically. The code will:
- Skip PyTorch-based OCRs (PaddleOCR/EasyOCR) to avoid DLL errors
- Use Tesseract directly for OCR processing
- Support PAN and Aadhaar document extraction

## Troubleshooting

If `tesseract --version` still doesn't work after installation:
1. Close and reopen PowerShell/terminal
2. Restart your computer (to refresh PATH)
3. Check if Tesseract is installed: Look for `C:\Program Files\Tesseract-OCR\tesseract.exe`
4. If file exists, use Method 4 to set `TESSERACT_CMD` environment variable

