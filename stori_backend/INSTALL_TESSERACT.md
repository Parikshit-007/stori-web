# Tesseract OCR Installation Guide for Windows

## Quick Installation Steps

### Option 1: Automatic Installer (Recommended)

1. **Download Tesseract OCR for Windows:**
   - Direct download: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.4.0.20240605.exe
   - Or from: https://github.com/UB-Mannheim/tesseract/wiki

2. **Run the installer:**
   - Run the downloaded `.exe` file
   - **IMPORTANT:** During installation, check the box **"Add to PATH"** 
   - Complete the installation

3. **Verify Installation:**
   ```powershell
   tesseract --version
   ```
   Should show version number (e.g., `tesseract 5.4.0`)

4. **Restart your Django server** after installation

### Option 2: Manual Path via Environment Variable

If Tesseract is installed but not in PATH, set environment variable:

**Windows (PowerShell):**
```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**Windows (CMD):**
```cmd
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

**Permanent (System Environment Variables):**
1. Open System Properties → Environment Variables
2. Add new variable:
   - Name: `TESSERACT_CMD`
   - Value: `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. Restart terminal/server

**Or in `.env` file (if using python-decouple):**
```
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Option 3: Chocolatey (if you have it)

```powershell
choco install tesseract
```

## After Installation

The code will automatically detect Tesseract in these locations:
- Environment variable: `TESSERACT_CMD`
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
- `C:\Tesseract-OCR\tesseract.exe`
- PATH environment variable

## Testing

After installation, restart your Django server and test the OCR API. Tesseract will be used as fallback when PaddleOCR/EasyOCR fail due to PyTorch DLL issues.

## Troubleshooting

If Tesseract is still not found:
1. Check if `tesseract.exe` exists in installation folder
2. Restart your terminal/IDE
3. Restart Django server
4. Check PATH: `echo $env:PATH` (PowerShell) or `echo %PATH%` (CMD)
5. Set `TESSERACT_CMD` environment variable with full path to `tesseract.exe`

