"""
KYC Document OCR API
Extracts structured data from PAN and Aadhaar documents using PaddleOCR
"""
import re
import cv2
import numpy as np
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
import logging

# Disable OneDNN to avoid compatibility issues on Windows
# Must be set before importing PaddleOCR/PaddlePaddle
os.environ['FLAGS_onednn'] = '0'
os.environ['ONEDNN_DISABLED'] = '1'
os.environ['DISABLE_MODEL_SOURCE_CHECK'] = 'True'
# Force CPU mode
os.environ['CUDA_VISIBLE_DEVICES'] = ''
# Additional flags to disable OneDNN/MKLDNN
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['MKLDNN_DISABLED'] = '1'

logger = logging.getLogger(__name__)

# Global OCR instance (initialized once)
_paddle_ocr = None
_easy_ocr = None
_tesseract_ocr = None  # Tesseract OCR (no PyTorch dependency, more stable on Windows)
USE_EASYOCR = False  # Set to True to use EasyOCR instead of PaddleOCR

# Configuration: Skip PyTorch-based OCRs if they keep failing (set to True to use only Tesseract)
SKIP_PYTORCH_OCR = True  # Set to True to skip PaddleOCR and EasyOCR (use only Tesseract)


def get_tesseract_ocr():
    """Get Tesseract OCR - no PyTorch dependency, most stable on Windows"""
    global _tesseract_ocr
    if _tesseract_ocr is None:
        try:
            import pytesseract
            from PIL import Image
            import os
            from decouple import config
            
            # Check for manual path in environment variable or settings
            manual_path = config('TESSERACT_CMD', default=None)
            if manual_path and os.path.exists(manual_path):
                pytesseract.pytesseract.tesseract_cmd = manual_path
                try:
                    pytesseract.get_tesseract_version()
                    logger.info(f"Tesseract found via TESSERACT_CMD env var: {manual_path}")
                    _tesseract_ocr = {'pytesseract': pytesseract, 'Image': Image}
                    return _tesseract_ocr
                except Exception as e:
                    logger.warning(f"TESSERACT_CMD path exists but tesseract failed: {str(e)}")
            
            # Try to auto-detect Tesseract in common Windows locations
            common_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
            ]
            
            tesseract_found = False
            found_path = None
            
            # First, try to get version (if already in PATH)
            try:
                pytesseract.get_tesseract_version()
                tesseract_found = True
                found_path = "PATH"
                logger.info("Tesseract found in PATH")
            except:
                # Not in PATH, try common installation paths
                for tesseract_path in common_paths:
                    if os.path.exists(tesseract_path):
                        pytesseract.pytesseract.tesseract_cmd = tesseract_path
                        try:
                            pytesseract.get_tesseract_version()
                            tesseract_found = True
                            found_path = tesseract_path
                            logger.info(f"Tesseract found at: {tesseract_path}")
                            break
                        except:
                            continue
            
            if not tesseract_found:
                # Provide a concise error message
                error_msg = (
                    "Tesseract OCR is not installed. Quick fix:\n"
                    "1. Download: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.4.0.20240605.exe\n"
                    "2. Install and check 'Add to PATH'\n"
                    "3. Restart server\n\n"
                    "OR set environment variable: TESSERACT_CMD=<path-to-tesseract.exe>"
                )
                logger.error(f"Tesseract not found. Checked paths: {', '.join(common_paths)}")
                raise Exception(error_msg)
            
            # Tesseract OCR doesn't need initialization, just return the module
            _tesseract_ocr = {'pytesseract': pytesseract, 'Image': Image}
            logger.info("Tesseract OCR initialized successfully")
        except ImportError as e:
            error_msg = f"Tesseract OCR Python package not installed. Install with: pip install pytesseract pillow. Error: {str(e)}"
            logger.error(error_msg)
            raise ImportError(error_msg)
        except Exception as e:
            # Re-raise if it's already our custom error message
            if "Tesseract binary not found" in str(e) or "Tesseract OCR Python package" in str(e):
                raise
            error_msg = f"Failed to initialize Tesseract OCR: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    return _tesseract_ocr


def get_easy_ocr():
    """Get or initialize EasyOCR instance (singleton pattern) - more stable on Windows"""
    global _easy_ocr
    if _easy_ocr is None:
        try:
            import easyocr
            # EasyOCR is more stable on Windows, no OneDNN issues
            _easy_ocr = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR initialized successfully")
        except ImportError as e:
            error_msg = f"EasyOCR not installed. Install with: pip install easyocr. Error: {str(e)}"
            logger.error(error_msg)
            raise ImportError(error_msg)
        except Exception as e:
            error_msg = f"Failed to initialize EasyOCR: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    return _easy_ocr


def get_paddle_ocr():
    """Get or initialize PaddleOCR instance (singleton pattern)"""
    global _paddle_ocr, USE_EASYOCR
    if _paddle_ocr is None:
        try:
            # Try to set PaddlePaddle device to CPU explicitly and disable OneDNN
            try:
                import paddle
                paddle.set_device('cpu')
                # Try to disable OneDNN in PaddlePaddle (API may vary by version)
                try:
                    paddle.fluid.core.set_onednn_enabled(False)
                except (AttributeError, ImportError):
                    # API might not exist in this version, try alternative
                    try:
                        import paddle.fluid as fluid
                        fluid.core.set_onednn_enabled(False)
                    except:
                        pass
            except Exception as e:
                # If paddle not available or method doesn't exist, continue
                logger.debug(f"Could not set PaddlePaddle device/OneDNN settings: {str(e)}")
            
            from paddleocr import PaddleOCR
            
            # Environment variables already set at module level
            # Initialize with minimal parameters - PaddleOCR 3.x has different API
            try:
                # Minimal initialization - just language
                _paddle_ocr = PaddleOCR(lang='en')
            except TypeError:
                # If lang parameter fails, try without any parameters
                try:
                    _paddle_ocr = PaddleOCR()
                except Exception as e2:
                    logger.error(f"PaddleOCR initialization failed: {str(e2)}")
                    raise
            except Exception as e:
                logger.error(f"PaddleOCR initialization error: {str(e)}")
                raise
            
            logger.info("PaddleOCR initialized successfully")
        except ImportError as e:
            error_msg = f"PaddleOCR not installed. Install with: pip install paddlepaddle paddleocr. Error: {str(e)}"
            logger.error(error_msg)
            # Try EasyOCR as fallback if PaddleOCR import fails
            logger.info("PaddleOCR import failed. Attempting to use EasyOCR as fallback...")
            try:
                return get_easy_ocr()
            except Exception as e2:
                raise ImportError(f"{error_msg}. EasyOCR fallback also failed: {str(e2)}")
        except Exception as e:
            error_msg = f"Failed to initialize PaddleOCR: {str(e)}"
            logger.error(error_msg)
            # Try EasyOCR as fallback if PaddleOCR initialization fails
            logger.info("PaddleOCR initialization failed. Attempting to use EasyOCR as fallback...")
            try:
                return get_easy_ocr()
            except Exception as e2:
                raise Exception(f"{error_msg}. EasyOCR fallback also failed: {str(e2)}")
    return _paddle_ocr


def extract_text_from_paddleocr(ocr_result):
    """
    Extract text from PaddleOCR result structure
    
    Args:
        ocr_result: PaddleOCR result
        
    Returns:
        Combined OCR text string
    """
    ocr_text_lines = []
    
    if not ocr_result:
        return ""
    
    if ocr_result is None:
        return ""
    
    if not isinstance(ocr_result, (list, tuple)):
        return ""
    
    # Handle result structure - could be nested or flat
    all_detections = []
    
    # Check if it's a list of pages
    if len(ocr_result) > 0 and isinstance(ocr_result[0], (list, tuple)):
        # It's a list of pages: [[detections...], ...]
        for page in ocr_result:
            if page and isinstance(page, (list, tuple)):
                all_detections.extend(page)
    else:
        # Single page or flat structure
        all_detections = ocr_result if isinstance(ocr_result, (list, tuple)) else [ocr_result]
    
    # Extract text from all detections
    for detection in all_detections:
        if not detection:
            continue
        
        try:
            # Detection should be: [bbox, (text, confidence)] or [bbox, text]
            if not isinstance(detection, (list, tuple)):
                continue
            
            if len(detection) < 2:
                continue
            
            text_data = detection[1]
            
            # Extract text from text_data
            text = None
            if isinstance(text_data, (list, tuple)):
                if len(text_data) > 0:
                    text = text_data[0]
            elif isinstance(text_data, str):
                text = text_data
            else:
                text = str(text_data) if text_data is not None else None
            
            if text and isinstance(text, str) and text.strip():
                ocr_text_lines.append(text.strip())
                
        except (IndexError, TypeError, AttributeError) as e:
            logger.debug(f"Skipping malformed OCR detection: {detection}, error: {str(e)}")
            continue
        except Exception as e:
            logger.warning(f"Unexpected error processing detection: {detection}, error: {str(e)}")
            continue
    
    return '\n'.join(ocr_text_lines)


def extract_text_from_easyocr(ocr_result):
    """
    Extract text from EasyOCR result structure
    
    Args:
        ocr_result: EasyOCR result (list of tuples: [(bbox, text, confidence), ...])
        
    Returns:
        Combined OCR text string
    """
    ocr_text_lines = []
    
    if not ocr_result:
        return ""
    
    for item in ocr_result:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            # EasyOCR format: (bbox, text, confidence)
            text = item[1]  # Second element is text
            if text and isinstance(text, str) and text.strip():
                ocr_text_lines.append(text.strip())
    
    return '\n'.join(ocr_text_lines)


def extract_text_from_tesseract(image_array):
    """
    Extract text from image using Tesseract OCR
    
    Args:
        image_array: numpy array image (BGR format from OpenCV)
        
    Returns:
        Combined OCR text string
    """
    try:
        tesseract_ocr = get_tesseract_ocr()
        pytesseract = tesseract_ocr['pytesseract']
        Image = tesseract_ocr['Image']
        
        # Convert BGR to RGB for PIL
        import cv2
        rgb_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # Run OCR
        text = pytesseract.image_to_string(pil_image, lang='eng')
        return text.strip()
    except Exception as e:
        logger.error(f"Tesseract OCR extraction failed: {str(e)}")
        raise


def preprocess_image(image_file):
    """
    Preprocess image using OpenCV for better OCR accuracy
    
    Args:
        image_file: Django uploaded file
        
    Returns:
        Preprocessed numpy array image (BGR format for PaddleOCR)
    """
    # Read image from file
    file_bytes = image_file.read()
    image_file.seek(0)  # Reset file pointer
    
    # Convert to numpy array
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Invalid image file. Could not decode image.")
    
    # PaddleOCR 3.x expects color images (BGR format with 3 channels)
    # Keep image in color format - minimal preprocessing
    
    # Ensure image has 3 channels (BGR format)
    if len(img.shape) == 2:
        # If grayscale, convert to BGR
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif len(img.shape) == 3:
        if img.shape[2] == 4:
            # If RGBA, convert to BGR
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        elif img.shape[2] == 1:
            # If single channel, convert to BGR
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        # If already 3 channels (BGR), keep as is
    
    # Optional: Light denoising on color image (preserves color channels)
    img = cv2.bilateralFilter(img, 9, 75, 75)
    
    # Optional: Resize if image is too large (PaddleOCR works better with reasonable sizes)
    height, width = img.shape[:2]
    max_dimension = 2000
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Final check: ensure 3-channel BGR format
    if len(img.shape) != 3 or img.shape[2] != 3:
        raise ValueError(f"Image must be in BGR format (3 channels), got shape: {img.shape}")
    
    return img


def extract_pan_fields(ocr_text):
    """
    Extract PAN fields from OCR text with improved bilingual support
    
    Args:
        ocr_text: Combined OCR text string
        
    Returns:
        Dictionary with extracted fields including name and father_name
    """
    import re
    import logging
    
    logger = logging.getLogger(__name__)
    
    result = {
        'pan_number': None,
        'dob': None,
        'name': None,
        'father_name': None
    }
    
    # Extract PAN number: 5 letters, 4 digits, 1 letter
    pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
    pan_matches = re.findall(pan_pattern, ocr_text.upper())
    if pan_matches:
        result['pan_number'] = pan_matches[0]
    
    # Extract DOB: DD/MM/YYYY or DD-MM-YYYY
    dob_patterns = [
        r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
        r'\b\d{2}\s+\d{2}\s+\d{4}\b'
    ]
    for pattern in dob_patterns:
        dob_matches = re.findall(pattern, ocr_text)
        if dob_matches:
            result['dob'] = dob_matches[0].replace(' ', '/')
            break
    
    # Split into lines
    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
    
    logger.info(f"Total lines: {len(lines)}")
    logger.info(f"OCR Lines: {lines}")
    
    # Common words to exclude
    exclude_words = {
        'income', 'tax', 'department', 'government', 'india', 'permanent',
        'account', 'number', 'card', 'signature', 'date', 'birth', 'photograph',
        'name', 'father', 'fathers', "father's"
    }
    
    # Devanagari/Hindi script detection
    def has_devanagari(text):
        """Check if text contains Devanagari/Hindi characters"""
        return bool(re.search(r'[\u0900-\u097F]', text))
    
    def is_mostly_english(text):
        """Check if text is mostly English characters"""
        english_chars = sum(1 for c in text if c.isascii() and (c.isalpha() or c.isspace()))
        total_alpha = sum(1 for c in text if c.isalpha() or c.isspace())
        return total_alpha > 0 and english_chars / total_alpha > 0.7
    
    def clean_line(line):
        """Remove common prefixes and clean the line"""
        # Remove Hindi/Devanagari characters
        line = re.sub(r'[\u0900-\u097F]+', '', line)
        
        # Remove common label patterns (more aggressive)
        line = re.sub(r'^.*?(name|father\'?s?\s+name)[\s:/|]*', '', line, flags=re.IGNORECASE)
        line = re.sub(r'[\s:/|]*(name|father\'?s?\s+name).*?$', '', line, flags=re.IGNORECASE)
        
        # Handle specific Hindi transliterations that OCR might produce
        line = re.sub(r'(पिता|का|नाम)', '', line, flags=re.IGNORECASE)
        
        # Remove leading/trailing special characters and extra spaces
        line = re.sub(r'^[^\w\s]+', '', line)
        line = re.sub(r'[^\w\s]+$', '', line)
        line = ' '.join(line.split())  # Normalize spaces
        
        return line.strip()
    
    def is_valid_name(text):
        """Validate if text is a valid name"""
        if not text or len(text) < 5:
            return False
        
        # Must be mostly English
        if not is_mostly_english(text):
            return False
        
        # Should have 2-5 words
        words = text.split()
        if len(words) < 2 or len(words) > 5:
            return False
        
        # Should be mostly alphabetic (allow spaces)
        # Count only alpha and spaces, ignore numbers that might be at the end
        alpha_space_count = sum(1 for c in text if c.isalpha() or c.isspace())
        total_chars = len(text)
        if total_chars > 0 and alpha_space_count / total_chars < 0.70:  # More lenient
            return False
        
        # Check for too many single-letter words (OCR garbage)
        single_letter_words = sum(1 for w in words if len(w) == 1)
        if single_letter_words > len(words) * 0.3:
            return False
        
        # Check if any word has numbers (but allow if at the end and will be cleaned)
        # Filter out words that are purely numeric
        alpha_words = [w for w in words if not w.isdigit()]
        if len(alpha_words) < 2:  # Need at least 2 actual name words
            return False
        
        # Check for exclude words - but only if they're standalone, not part of a name
        text_lower = text.lower()
        text_words = set(w.lower() for w in alpha_words)
        if text_words.intersection(exclude_words):
            return False
        
        return True
    
    def remove_trailing_numbers(text):
        """Remove trailing numbers from text (e.g., 'SUSHIL PANDEY 15042022' -> 'SUSHIL PANDEY')"""
        if not text:
            return text
        # Remove trailing digits and spaces
        text = re.sub(r'\s+\d+\s*$', '', text)
        # Also remove any trailing standalone numbers
        text = re.sub(r'\s+\d{4,}\s*$', '', text)  # Remove 4+ digit numbers at the end
        return text.strip()
    
    def extract_name_from_line(line, label_keyword=None):
        """Extract name from a line that may contain labels"""
        # Handle "नाम/Name PARIKSHIT SUSHIL PANDEY" pattern
        if '/' in line:
            parts = line.split('/')
            for part in parts:
                cleaned = clean_line(part)
                # Remove trailing numbers before validation
                cleaned = remove_trailing_numbers(cleaned)
                if is_valid_name(cleaned):
                    return cleaned
        
        # Handle "Name: PARIKSHIT SUSHIL PANDEY" pattern
        if ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                cleaned = clean_line(parts[1])
                # Remove trailing numbers before validation
                cleaned = remove_trailing_numbers(cleaned)
                if is_valid_name(cleaned):
                    return cleaned
        
        # Try cleaning the whole line
        cleaned = clean_line(line)
        # Remove trailing numbers before validation
        cleaned = remove_trailing_numbers(cleaned)
        if is_valid_name(cleaned):
            return cleaned
        
        return None
    
    # Find reference indices
    pan_idx = None
    name_label_idx = None
    father_label_idx = None
    dob_idx = None
    
    for i, line in enumerate(lines):
        line_upper = line.upper()
        
        # Find PAN line
        if result['pan_number'] and result['pan_number'] in line_upper:
            pan_idx = i
            logger.info(f"Found PAN at line {i}: {line}")
        
        # Find DOB line
        if result['dob'] and result['dob'].replace('/', '-') in line:
            dob_idx = i
            logger.info(f"Found DOB at line {i}: {line}")
        
        # Find Name label (check for both English and pattern)
        if re.search(r'\bname\b', line, re.IGNORECASE) and not re.search(r"father", line, re.IGNORECASE):
            # This might be name line or just label
            name_label_idx = i
            logger.info(f"Found 'Name' label at line {i}: {line}")
        
        # Find Father's Name label
        if re.search(r"father'?s?\s+name", line, re.IGNORECASE):
            father_label_idx = i
            logger.info(f"Found 'Father's Name' label at line {i}: {line}")
    
    # Extract Name
    # Strategy 1: Check line with "Name" label
    if name_label_idx is not None:
        name = extract_name_from_line(lines[name_label_idx])
        if name:
            result['name'] = name
            logger.info(f"Extracted name from label line: {name}")
    
    # Strategy 2: Check line after "Name" label
    if not result['name'] and name_label_idx is not None and name_label_idx + 1 < len(lines):
        next_line = lines[name_label_idx + 1]
        name = extract_name_from_line(next_line)
        if name:
            result['name'] = name
            logger.info(f"Extracted name from line after label: {name}")
    
    # Strategy 3: Check lines above PAN (typically 1-3 lines above)
    if not result['name'] and pan_idx is not None:
        for offset in range(1, min(5, pan_idx + 1)):
            idx = pan_idx - offset
            line = lines[idx]
            name = extract_name_from_line(line)
            if name:
                # Make sure it's not father's name line
                if not re.search(r"father", line, re.IGNORECASE):
                    result['name'] = name
                    logger.info(f"Extracted name from line {idx} (above PAN): {name}")
                    break
    
    # Extract Father's Name
    # Strategy 1: Check line with "Father's Name" label
    if father_label_idx is not None:
        # First, try to extract from the same line
        father_name = extract_name_from_line(lines[father_label_idx], label_keyword='father')
        if father_name:
            result['father_name'] = father_name
            logger.info(f"Extracted father's name from label line: {father_name}")
        
        # Also check the next line (father's name often on next line)
        if not result['father_name'] and father_label_idx + 1 < len(lines):
            next_line = lines[father_label_idx + 1]
            logger.info(f"Checking next line after father label: {next_line}")
            father_name = extract_name_from_line(next_line)
            if father_name:
                result['father_name'] = father_name
                logger.info(f"Extracted father's name from line after label: {father_name}")
    
    # Strategy 2: Look between name and DOB/signature - specifically check for lines with 3 words
    if not result['father_name'] and name_label_idx is not None:
        # Father's name is usually between Name and DOB
        search_end = dob_idx if dob_idx else len(lines)
        for idx in range(name_label_idx + 1, min(search_end, name_label_idx + 5)):
            if idx >= len(lines):
                break
            line = lines[idx]
            logger.info(f"Checking line {idx} between name and DOB: {line}")
            
            # Skip if it's the cardholder's name
            if result['name'] and result['name'].upper() in line.upper():
                continue
            
            # Check if this line mentions father
            if re.search(r"father", line, re.IGNORECASE):
                father_name = extract_name_from_line(line, label_keyword='father')
                if father_name:
                    result['father_name'] = father_name
                    logger.info(f"Extracted father's name from line {idx} with 'father' keyword: {father_name}")
                    break
            else:
                # Try extracting even without father keyword
                cleaned = clean_line(line)
                logger.info(f"Cleaned line {idx}: {cleaned}")
                if is_valid_name(cleaned):
                    result['father_name'] = cleaned
                    logger.info(f"Extracted father's name from line {idx}: {cleaned}")
                    break
    
    # Strategy 4: Aggressive search - look for any line with valid name after the cardholder's name
    if not result['father_name'] and name_label_idx is not None:
        logger.warning("Trying aggressive father name search...")
        # Search lines after name label but before DOB
        search_start = name_label_idx + 1
        search_end = dob_idx if dob_idx else min(name_label_idx + 6, len(lines))
        
        for idx in range(search_start, search_end):
            if idx >= len(lines):
                break
            line = lines[idx]
            logger.info(f"Checking line {idx} for father's name: {line}")
            
            # Skip if it's the cardholder's name
            if result['name'] and result['name'].upper() in line.upper():
                continue
            
            # Try to extract any valid name
            father_name = extract_name_from_line(line)
            if father_name:
                result['father_name'] = father_name
                logger.info(f"Extracted father's name from line {idx} (aggressive search): {father_name}")
                break
    
    # Strategy 5: Look for pattern like "SUSHIL SESHMANI PANDEY" anywhere in text
    if not result['father_name']:
        logger.warning("Trying pattern-based father name search...")
        # Look for lines with 2-4 words, all caps, after name has been found
        if result['name']:
            name_found = False
            for i, line in enumerate(lines):
                # Check if we've passed the name line
                if result['name'].upper() in line.upper():
                    name_found = True
                    continue
                
                if name_found:
                    # Look for potential father's name
                    cleaned = clean_line(line)
                    if is_valid_name(cleaned) and cleaned.upper() != result['name'].upper():
                        result['father_name'] = cleaned
                        logger.info(f"Extracted father's name from line {i} (pattern search): {cleaned}")
                        break
    
    # Fallback: Scan all lines for valid names
    if not result['name']:
        logger.warning("Name not found, scanning all lines...")
        for i, line in enumerate(lines):
            # Skip lines that are clearly not names
            if has_devanagari(line):
                continue
            if result['pan_number'] and result['pan_number'] in line.upper():
                continue
            if result['dob'] and result['dob'] in line:
                continue
            
            name = extract_name_from_line(line)
            if name and not re.search(r"father", line, re.IGNORECASE):
                result['name'] = name
                logger.info(f"Extracted name from line {i} (fallback): {name}")
                break
    
    # Format names to title case if all uppercase
    if result['name']:
        # Remove trailing numbers
        result['name'] = remove_trailing_numbers(result['name'])
        if result['name'].isupper():
            result['name'] = result['name'].title()
        # Remove extra spaces
        result['name'] = ' '.join(result['name'].split())
    
    if result['father_name']:
        # Remove trailing numbers
        result['father_name'] = remove_trailing_numbers(result['father_name'])
        if result['father_name'].isupper():
            result['father_name'] = result['father_name'].title()
        # Remove extra spaces
        result['father_name'] = ' '.join(result['father_name'].split())
    
    logger.info(f"Final extraction: {result}")
    
    return result


def extract_pan_fields_old_backup(ocr_text):
    """
    Extract PAN fields from OCR text
    
    Args:
        ocr_text: Combined OCR text string
        
    Returns:
        Dictionary with extracted fields
    """
    result = {
        'pan_number': None,
        'dob': None,
        'name': None
    }
    
    # Extract PAN number: 5 letters, 4 digits, 1 letter
    pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
    pan_matches = re.findall(pan_pattern, ocr_text.upper())
    if pan_matches:
        result['pan_number'] = pan_matches[0]
    
    # Extract DOB: DD/MM/YYYY or DD-MM-YYYY
    dob_patterns = [
        r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
        r'\b\d{2}\s+\d{2}\s+\d{4}\b'
    ]
    for pattern in dob_patterns:
        dob_matches = re.findall(pattern, ocr_text)
        if dob_matches:
            result['dob'] = dob_matches[0].replace(' ', '/')
            break
    
    # Extract name: Filter out common PAN card header/footer text
    # Common text to exclude
    exclude_patterns = [
        r'permanent\s+account\s+number',
        r'income\s+tax\s+department',
        r'government\s+of\s+india',
        r'father\'?s?\s+name',
        r'father\s+name',
        r'father\'?s?\s+neme',  # OCR error variant
        r'income\s+tax',
        r'account\s+number',
        r'card',
        r'^pan\b',
        r'date\s+of\s+birth',
        r'signature',
        r'photograph',
        r'name\s*:',  # Lines that are labels, not actual names
        r'^name$',  # Just the word "name"
    ]
    
    # Additional patterns that indicate this is NOT a name line
    not_name_indicators = [
        '/',  # Lines with slashes often contain labels
        ':',  # Lines with colons are usually labels
        'father',
        'mother',
        'guardian',
    ]
    
    # OCR garbage patterns - lines that look like OCR errors
    ocr_garbage_patterns = [
        r'^[A-Za-z]{1,2}\s+[A-Za-z]{1,2}\s+[A-Za-z]{1,2}',  # Very short words (likely OCR errors)
        r'[A-Za-z]{1}\s+[A-Za-z]{1}',  # Single letter words
        r'^[A-Z]{1,2}\s+[A-Z]{1,2}\s+[A-Z]{1,2}\s+[A-Z]{1,2}',  # Multiple single/double uppercase letters
        r'^[a-z]+\s+[A-Z]{1,2}\s+[A-Z]{1,3}\s+[A-Z]{1,2}',  # Pattern like "eared Sa AeA TS" (lowercase start + short uppercase)
        r'^[a-z]+\s+[A-Z]{1,2}\s+[A-Z]{1,2}$',  # Pattern like "eared Sa TS" (lowercase + 2 short uppercase)
        r'^[a-z]+\s+[A-Z]{1,2}\s+[A-Z]{1,3}\s+[A-Z]{1,2}$',  # Exact match for "eared Sa AeA TS"
    ]
    
    lines = ocr_text.split('\n')
    dob_line_idx = None
    pan_line_idx = None
    
    # Find line containing DOB
    if result['dob']:
        for i, line in enumerate(lines):
            dob_variants = [
                result['dob'],
                result['dob'].replace('/', '-'),
                result['dob'].replace('-', '/'),
            ]
            if any(dob_var in line for dob_var in dob_variants):
                dob_line_idx = i
                break
    
    # Find line containing PAN number (name is usually above PAN)
    if result['pan_number']:
        for i, line in enumerate(lines):
            if result['pan_number'] in line.upper():
                pan_line_idx = i
                break
    
    # Look for name in lines before DOB or PAN (usually 1-3 lines above)
    best_name = None
    best_score = 0
    
    # Strategy: Look around PAN number first (more reliable), then around DOB
    search_ranges = []
    
    # Priority 1: Look around PAN number (name is usually above PAN)
    if pan_line_idx is not None:
        # Look 1-6 lines above PAN (increased range to catch name)
        search_ranges.append((pan_line_idx - 1, max(-1, pan_line_idx - 7)))
    
    # Priority 2: Look around DOB (if PAN not found or no name found)
    if dob_line_idx is not None:
        # Look 1-4 lines above DOB
        search_ranges.append((dob_line_idx - 1, max(-1, dob_line_idx - 5)))
    
    # Search in priority order
    for start_idx, end_idx in search_ranges:
        if start_idx < 0:
            continue
        # Search in lines before the reference line
        for i in range(start_idx, end_idx, -1):
            line = lines[i].strip()
            if not line:
                continue
            
            # Skip if line matches exclude patterns
            line_lower = line.lower()
            if any(re.search(pattern, line_lower) for pattern in exclude_patterns):
                continue
            
            # Calculate distance from PAN/DOB for leniency
            distance = 999
            if pan_line_idx is not None:
                distance = abs(i - pan_line_idx)
            elif dob_line_idx is not None:
                distance = abs(i - dob_line_idx)
            
            # Skip OCR garbage patterns - but be more lenient if close to PAN
            # Some OCR garbage patterns might actually be names with poor OCR quality
            if distance > 3:  # Only apply strict garbage filtering if far from PAN
                if any(re.search(pattern, line) for pattern in ocr_garbage_patterns):
                    continue
            
            # Skip lines with too many single/double character words (OCR errors) - but be less strict
            words = line.split()
            short_words = sum(1 for w in words if len(w) <= 2)
            short_word_threshold = 0.8 if distance <= 3 else 0.7  # Very lenient if close to PAN
            if len(words) > 0 and short_words / len(words) > short_word_threshold:
                continue
            
            # Skip lines with too many special characters
            special_chars = sum(1 for c in line if c in '|[]{}()&@#$%^*+=_~`')
            if len(line) > 0 and special_chars / len(line) > 0.2:  # More than 20% special chars
                continue
            
            # If line contains "/", handle it properly
            # Pattern 1: "नाम / Name" or "Name / नाम" - label before/after name
            # Pattern 2: "PARIKSHIT SUSHIL PANDEY / Name" - name before label
            # Pattern 3: "Name / PARIKSHIT SUSHIL PANDEY" - name after label
            if '/' in line:
                parts = [p.strip() for p in line.split('/')]
                if len(parts) >= 2:
                    # Check each part to find the actual name
                    name_candidate = None
                    for part in parts:
                        part_lower = part.lower().strip()
                        # Skip if part is just a label word
                        if part_lower in ['name', 'नाम', 'father', 'mother', 'guardian', 'पिता', 'माता']:
                            continue
                        # If part looks like a name (has 2+ words, reasonable length)
                        part_words = part.split()
                        if len(part_words) >= 2 and len(part) >= 8:
                            # Check if it's not just label text
                            if not any(label in part_lower for label in ['name', 'father', 'mother', 'guardian', 'नाम', 'पिता', 'माता']):
                                name_candidate = part
                                break
                    
                    if name_candidate:
                        line = name_candidate
                        line_lower = line.lower()
                    else:
                        # Fallback: if second part is label, take first part
                        second_part_lower = parts[1].lower().strip()
                        if second_part_lower in ['name', 'नाम', 'father', 'mother', 'guardian']:
                            line = parts[0].strip()
                            # If first part is too short or looks like garbage, skip this line
                            if len(line) < 6 or any(re.search(pattern, line) for pattern in ocr_garbage_patterns):
                                continue
                            line_lower = line.lower()
                        else:
                            # If first part is label, take second part
                            first_part_lower = parts[0].lower().strip()
                            if first_part_lower in ['name', 'नाम', 'father', 'mother', 'guardian']:
                                line = parts[1].strip()
                                if len(line) < 6 or any(re.search(pattern, line) for pattern in ocr_garbage_patterns):
                                    continue
                                line_lower = line.lower()
            
            # Skip if line contains not-name indicators (after split)
            if any(indicator in line_lower for indicator in not_name_indicators):
                continue
            
            # Clean line: remove common prefixes/suffixes
            cleaned_line = re.sub(r'^(name|father|mother|guardian)[\s:]*', '', line, flags=re.IGNORECASE).strip()
            if not cleaned_line or cleaned_line == line.lower():
                cleaned_line = line
            
            # Name usually has 2-6 words (First Name, Middle Name, Last Name) - Indian names can be longer
            words = [w.strip() for w in cleaned_line.split() if w.strip()]
            if 2 <= len(words) <= 6:
                # REJECT "eared Sa AeA TS" pattern IMMEDIATELY - it's always garbage
                # Pattern: lowercase first word + all remaining words are very short (<=3) uppercase
                if len(words) >= 3 and words[0][0].islower() and all(len(w) <= 3 and w[0].isupper() for w in words[1:]):
                    # Exception: if first word is long (>=5) and all words are reasonable (>=4), might be name
                    if not (len(words[0]) >= 5 and all(len(w) >= 4 for w in words[1:])):
                        logger.debug(f"Rejecting garbage pattern at line {i}: {cleaned_line}")
                        continue  # Skip this line completely
                
                # Calculate distance from PAN/DOB for leniency
                distance = 999
                if pan_line_idx is not None:
                    distance = abs(i - pan_line_idx)
                elif dob_line_idx is not None:
                    distance = abs(i - dob_line_idx)
                
                # Skip if too many very short words (OCR errors) - but be less strict if close to PAN
                short_word_ratio = sum(1 for w in words if len(w) <= 2) / len(words) if len(words) > 0 else 0
                short_word_threshold = 0.7 if distance <= 3 else 0.6  # More lenient if close
                if short_word_ratio > short_word_threshold:
                    continue
                
                # Check if most words start with capital letter - be more lenient if close to PAN
                # Also accept if at least one word is capitalized (for OCR errors where name is lowercase)
                capitalized = sum(1 for w in words if w and w[0].isupper())
                capitalization_threshold = 0.2 if distance <= 3 else 0.5  # Very lenient if close (accept if 20% capitalized)
                if capitalized >= len(words) * capitalization_threshold or (distance <= 3 and capitalized >= 1):
                    # REJECT "eared Sa AeA TS" pattern completely BEFORE scoring - it's always garbage
                    # Pattern: lowercase first word + all remaining words are very short (<=3) uppercase
                    if len(words) >= 3 and words[0][0].islower() and all(len(w) <= 3 and w[0].isupper() for w in words[1:]):
                        # Exception: if first word is long (>=5) and all words are reasonable (>=4), might be name
                        if not (len(words[0]) >= 5 and all(len(w) >= 4 for w in words[1:])):
                            logger.debug(f"Rejecting garbage pattern at line {i}: {cleaned_line}")
                            continue  # Skip this line completely
                    
                    # Skip very short names (likely OCR errors)
                    min_length = 6 if distance <= 3 else 8  # More lenient if close
                    if len(cleaned_line) >= min_length:
                        # Final check: should not contain common label words
                        if not any(word.lower() in ['name', 'father', 'mother', 'guardian'] for word in words):
                            # Additional check: words should be reasonable length (not all 1-2 chars)
                            avg_word_length = sum(len(w) for w in words) / len(words) if len(words) > 0 else 0
                            min_avg_length = 2.0 if distance <= 3 else 2.5  # More lenient if close
                            if avg_word_length >= min_avg_length:
                                # Score: prefer longer names (3-4 words are common for Indian names)
                                name_score = len(words) * 10  # Longer names get higher score
                                
                                # Prefer all uppercase (like "PARIKSHIT SUSHIL PANDEY") over mixed case
                                if cleaned_line.isupper() and all(len(w) >= 4 for w in words):
                                    name_score += 30  # Strong preference for proper uppercase names
                                elif not cleaned_line.isupper():
                                    name_score += 20  # Prefer mixed case over all uppercase
                                
                                if len(cleaned_line) >= 12:  # Prefer longer names (relaxed from 15)
                                    name_score += 10
                                if avg_word_length >= 4.0:  # Prefer names with longer words (increased from 3.5)
                                    name_score += 15
                                elif avg_word_length >= 3.5:
                                    name_score += 10
                                
                                # Bonus for being close to PAN
                                if distance <= 3:
                                    name_score += 15
                                
                                if name_score > best_score:
                                    best_name = cleaned_line
                                    best_score = name_score
                                    logger.debug(f"Found candidate name at line {i}: {cleaned_line} (score: {name_score}, distance: {distance})")
        
        # If we found a good name, stop searching
        if best_name and best_score >= 30:  # Good quality name found
            break
    
    if best_name:
        result['name'] = best_name
        logger.debug(f"PAN name extracted from reference line area: {best_name}")
    else:
        logger.debug(f"PAN name not found near DOB/PAN line. DOB line idx: {dob_line_idx}, PAN line idx: {pan_line_idx}")
    
    # Fallback: Look for name pattern in all lines (excluding headers/footers)
    if not result['name']:
        logger.debug("Trying fallback: searching all lines for name pattern...")
        candidate_names = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip exclude patterns
            line_lower = line.lower()
            if any(re.search(pattern, line_lower) for pattern in exclude_patterns):
                continue
            
            # Skip OCR garbage patterns
            if any(re.search(pattern, line) for pattern in ocr_garbage_patterns):
                continue
            
            # Skip lines with too many single/double character words (OCR errors)
            words_check = line.split()
            short_words = sum(1 for w in words_check if len(w) <= 2)
            if len(words_check) > 0 and short_words / len(words_check) > 0.5:
                continue
            
            # Skip lines with too many special characters
            special_chars = sum(1 for c in line if c in '|[]{}()&@#$%^*+=_~`')
            if len(line) > 0 and special_chars / len(line) > 0.2:
                continue
            
            # If line contains "/", split and take the first part (before label)
            if '/' in line:
                parts = line.split('/')
                if len(parts) > 1:
                    # Check if second part contains label indicators
                    second_part_lower = parts[1].lower()
                    if any(indicator in second_part_lower for indicator in ['father', 'mother', 'guardian', 'name']):
                        line = parts[0].strip()  # Take first part as name
                        line_lower = line.lower()
            
            # Skip if line contains not-name indicators (after split)
            if any(indicator in line_lower for indicator in not_name_indicators):
                continue
            
            # Skip if all uppercase and too long (likely header)
            if line.isupper() and len(line) > 25:
                continue
            
            # Clean line
            cleaned_line = re.sub(r'^(name|father|mother|guardian)[\s:]*', '', line, flags=re.IGNORECASE).strip()
            if not cleaned_line or cleaned_line == line.lower():
                cleaned_line = line
            
            words = [w.strip() for w in cleaned_line.split() if w.strip()]
            if 2 <= len(words) <= 6:
                # Skip if too many very short words - but be less strict
                short_word_ratio = sum(1 for w in words if len(w) <= 2) / len(words) if len(words) > 0 else 0
                if short_word_ratio > 0.6:  # More than 60% short words (relaxed from 40%)
                    continue
                
                # Skip if contains label words
                if any(word.lower() in ['name', 'father', 'mother', 'guardian'] for word in words):
                    continue
                
                capitalized = sum(1 for w in words if w and w[0].isupper())
                if capitalized >= len(words) * 0.5:  # 50% of words capitalized (relaxed from 60%)
                    # Check average word length
                    avg_word_length = sum(len(w) for w in words) / len(words) if len(words) > 0 else 0
                    if avg_word_length >= 2.5 and len(cleaned_line) >= 8:  # Minimum reasonable length (relaxed)
                        # Prefer longer names (3-4 words), mixed case, and reasonable length
                        score = len(words) * 10  # Longer names get higher score
                        if not cleaned_line.isupper():
                            score += 20  # Prefer mixed case
                        if len(cleaned_line) >= 12:  # Prefer longer names (relaxed from 15)
                            score += 10
                        if avg_word_length >= 3.5:  # Prefer names with longer words (relaxed from 4)
                            score += 10
                        candidate_names.append((cleaned_line, score))
        
        if candidate_names:
            # Get best candidate (longest, preferably not all uppercase, with longer words)
            result['name'] = max(candidate_names, key=lambda x: x[1])[0]
    
    # Final fallback: If still no name found, try very lenient matching
    # This is a last resort to extract something that looks like a name
    # But be more careful to avoid OCR garbage
    if not result['name']:
        logger.warning("No name found with standard extraction, trying lenient fallback...")
        lenient_candidates = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            # Calculate distance from PAN/DOB for leniency
            distance = 999
            if pan_line_idx is not None:
                distance = abs(i - pan_line_idx)
            elif dob_line_idx is not None:
                distance = abs(i - dob_line_idx)
            
            # Be more lenient with minimum length if close to PAN
            min_length = 6 if distance <= 7 else 8
            if not line or len(line) < min_length:
                continue
            
            line_lower = line.lower()
            # Skip obvious non-name lines
            if any(keyword in line_lower for keyword in ['permanent', 'account', 'number', 'income', 'tax', 'government', 'india', 'father', 'mother', 'guardian', 'date', 'birth', 'signature', 'photograph']):
                continue
            
            # Skip if contains DOB or PAN
            if result['dob'] and result['dob'].replace('/', '-') in line:
                continue
            if result['pan_number'] and result['pan_number'] in line.upper():
                continue
            
            # Handle lines with "/" - properly extract name from label/name combinations
            original_line = line
            if '/' in line:
                parts = [p.strip() for p in line.split('/')]
                if len(parts) >= 2:
                    # Check each part to find the actual name
                    name_candidate = None
                    for part in parts:
                        part_lower = part.lower().strip()
                        # Skip if part is just a label word
                        if part_lower in ['name', 'नाम', 'father', 'mother', 'guardian', 'पिता', 'माता']:
                            continue
                        # If part looks like a name (has 2+ words, reasonable length)
                        part_words = part.split()
                        if len(part_words) >= 2 and len(part) >= 8:
                            # Check if it's not just label text
                            if not any(label in part_lower for label in ['name', 'father', 'mother', 'guardian', 'नाम', 'पिता', 'माता']):
                                name_candidate = part
                                break
                    
                    if name_candidate:
                        line = name_candidate
                    else:
                        # Fallback: if second part is label, take first part
                        second_part_lower = parts[1].lower().strip()
                        if second_part_lower in ['name', 'नाम', 'father', 'mother', 'guardian']:
                            line = parts[0].strip()
                            # If first part is too short or looks like garbage, skip
                            if len(line) < 6 or any(re.search(pattern, line) for pattern in ocr_garbage_patterns):
                                continue
                        else:
                            # If first part is label, take second part
                            first_part_lower = parts[0].lower().strip()
                            if first_part_lower in ['name', 'नाम', 'father', 'mother', 'guardian']:
                                line = parts[1].strip()
                                if len(line) < 6 or any(re.search(pattern, line) for pattern in ocr_garbage_patterns):
                                    continue
            
            # Skip if line ends with label words like "Name", "Father's Name", etc.
            line_lower = line.lower().strip()
            if line_lower.endswith((' name', '/name', ':name', ' name:', '/ name')):
                # Try to extract name before the label
                line = re.sub(r'[/:]\s*name\s*$', '', line, flags=re.IGNORECASE).strip()
                if len(line) < 6:
                    continue
            
            # Skip lines with too many special chars
            special_chars = sum(1 for c in line if c in '|[]{}()&@#$%^*+=_~`')
            if len(line) > 0 and special_chars / len(line) > 0.25:  # 25% threshold
                continue
            
            # Skip OCR garbage patterns
            if any(re.search(pattern, line) for pattern in ocr_garbage_patterns):
                continue
            
            # Skip if line contains standalone "Name" as a word (it's a label, not part of name)
            # But be careful - if line is like "John Doe / Name", we already handled the "/" split above
            words = line.split()
            # Only skip if "name" is a standalone word and line is very short
            if 'name' in [w.lower() for w in words] and len(words) <= 2:
                # If "name" is in the line and it's a very short line (1-2 words), likely a label
                continue
            
            if 2 <= len(words) <= 6:
                # Check distance from PAN/DOB to adjust strictness
                distance = 999
                if pan_line_idx is not None:
                    distance = abs(i - pan_line_idx)
                elif dob_line_idx is not None:
                    distance = abs(i - dob_line_idx)
                
                # Check for too many single/double char words (OCR garbage)
                # Be more lenient if close to PAN/DOB (likely actual name)
                short_words = sum(1 for w in words if len(w) <= 2)
                short_word_threshold = 0.5 if distance <= 3 else 0.4  # More lenient if close
                if len(words) > 0 and short_words / len(words) > short_word_threshold:
                    continue
                
                # Check for pattern like "eared Sa AeA TS" - starts with lowercase, then short uppercase words
                # This is almost always garbage, even if close to PAN
                if len(words) >= 3:
                    # If first word is lowercase and rest are very short uppercase (<=3 chars), likely garbage
                    if words[0][0].islower() and all(len(w) <= 3 and w[0].isupper() for w in words[1:]):
                        # Exception: if first word is long (>=5 chars) and all words are reasonable length, might be name
                        if not (len(words[0]) >= 5 and all(len(w) >= 4 for w in words[1:])):
                            continue
                
                # Check for pattern like "aTa" - very short mixed case words (likely OCR garbage)
                if len(words) >= 1:
                    # If first word is very short (<=3 chars) and mixed case (not all upper/lower), likely garbage
                    first_word = words[0]
                    if len(first_word) <= 3 and first_word.isalpha() and not first_word.isupper() and not first_word.islower():
                        # Mixed case short word like "aTa" - likely OCR garbage
                        continue
                
                # Very lenient: check if it has some capitalized words OR if close to PAN (might be lowercase OCR error)
                capitalized = sum(1 for w in words if w and w[0].isupper())
                
                # If close to PAN/DOB, accept even if mostly lowercase (OCR might have read name as lowercase)
                capitalization_ok = False
                if distance <= 7:  # Increased range to 7 lines (name can be several lines above PAN)
                    # Very lenient: accept if at least 1 word capitalized OR if all words are reasonable length (might be lowercase name)
                    # Also accept if line has 3+ words and reasonable average length (likely a name)
                    # "sae faant ana Wa" has 4 words, 1 capitalized, avg length ~3.25 - should pass
                    capitalization_ok = (capitalized >= 1) or (capitalized >= 0 and all(len(w) >= 3 for w in words)) or (len(words) >= 3 and sum(len(w) for w in words) / len(words) >= 2.5)
                else:
                    # Further away: require at least 40% capitalized
                    capitalization_ok = capitalized >= len(words) * 0.4
                
                if capitalization_ok:
                    # Check if average word length is reasonable
                    avg_length = sum(len(w) for w in words) / len(words) if len(words) > 0 else 0
                    # If close to PAN/DOB (within 7 lines), be more lenient with avg_length
                    min_avg_length = 2.0 if distance <= 7 else 3.0  # Very lenient if close
                    if avg_length >= min_avg_length:
                        # Prefer lines closer to PAN/DOB
                        distance_score = 0
                        if pan_line_idx is not None:
                            distance = abs(i - pan_line_idx)
                            if distance <= 5:
                                distance_score = 30 - (distance * 3)  # Closer = higher score (increased weight)
                        elif dob_line_idx is not None:
                            distance = abs(i - dob_line_idx)
                            if distance <= 5:
                                distance_score = 30 - (distance * 3)
                        
                        # Score based on quality - prefer longer words, closer to PAN/DOB
                        score = len(words) * 5 + avg_length * 10 + distance_score  # Increased avg_length weight
                        if not line.isupper():
                            score += 10
                        # Penalize if has too many short words even if passed threshold (but less penalty if close)
                        if short_words / len(words) > 0.3:
                            penalty = 5 if distance <= 3 else 10  # Less penalty if close to PAN/DOB
                            score -= penalty
                        
                        logger.debug(f"Lenient candidate at line {i}: '{line}' (score: {score}, distance: {distance}, avg_length: {avg_length:.2f})")
                        lenient_candidates.append((line, score, i))
        
        if lenient_candidates:
            # Get best candidate (highest score)
            best_candidate = max(lenient_candidates, key=lambda x: x[1])
            result['name'] = best_candidate[0]
            logger.info(f"Extracted name using lenient fallback: {best_candidate[0]} (score: {best_candidate[1]}, line: {best_candidate[2]})")
        else:
            logger.warning(f"No lenient candidates found. PAN line: {pan_line_idx}, DOB line: {dob_line_idx}. Total lines: {len(lines)}")
            # Log lines around PAN for debugging
            if pan_line_idx is not None:
                start = max(0, pan_line_idx - 5)
                end = min(len(lines), pan_line_idx + 2)
                logger.debug(f"Lines around PAN (line {pan_line_idx}): {lines[start:end]}")
    
    return result


def extract_aadhaar_front_fields(ocr_text):
    """
    Extract Aadhaar front fields from OCR text
    
    Args:
        ocr_text: Combined OCR text string
        
    Returns:
        Dictionary with extracted fields
    """
    result = {
        'aadhaar_number': None,
        'gender': None,
        'dob': None,
        'yob': None,
        'name': None
    }
    
    # Extract Aadhaar number: 4 digits, space, 4 digits, space, 4 digits
    aadhaar_patterns = [
        r'\b\d{4}\s+\d{4}\s+\d{4}\b',
        r'\b\d{4}\s?\d{4}\s?\d{4}\b',
        r'\b\d{12}\b'  # Without spaces
    ]
    
    for pattern in aadhaar_patterns:
        matches = re.findall(pattern, ocr_text)
        if matches:
            # Format as 4-4-4
            aadhaar = matches[0].replace(' ', '')
            if len(aadhaar) == 12:
                result['aadhaar_number'] = f"{aadhaar[:4]} {aadhaar[4:8]} {aadhaar[8:]}"
            else:
                result['aadhaar_number'] = matches[0]
            break
    
    # Extract gender: Look for MALE, FEMALE, M, F
    gender_patterns = [
        (r'\b(MALE|M)\b', 'MALE'),
        (r'\b(FEMALE|F)\b', 'FEMALE'),
        (r'\b(OTHER|O)\b', 'OTHER')
    ]
    
    for pattern, gender in gender_patterns:
        if re.search(pattern, ocr_text, re.IGNORECASE):
            result['gender'] = gender
            break
    
    # Extract DOB or YOB
    # DOB patterns
    dob_patterns = [
        r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
        r'\b\d{2}\s+\d{2}\s+\d{4}\b'
    ]
    for pattern in dob_patterns:
        matches = re.findall(pattern, ocr_text)
        if matches:
            result['dob'] = matches[0].replace(' ', '/')
            break
    
    # YOB pattern (4 digits, usually near DOB)
    yob_pattern = r'\b(19|20)\d{2}\b'
    yob_matches = re.findall(yob_pattern, ocr_text)
    if yob_matches and not result['dob']:
        # Take most recent year that makes sense
        current_year = timezone.now().year
        valid_yobs = [int(y) for y in yob_matches if 1900 <= int(y) <= current_year]
        if valid_yobs:
            result['yob'] = str(max(valid_yobs))
    
    # Extract name: Usually appears prominently, look for capitalized words
    lines = ocr_text.split('\n')
    candidate_names = []
    
    for line in lines:
        line = line.strip()
        # Skip lines with numbers (likely not name)
        if re.search(r'\d', line):
            continue
        
        words = line.split()
        # Name usually 2-5 words, mostly capitalized
        if 2 <= len(words) <= 5:
            capitalized = sum(1 for w in words if w and w[0].isupper())
            if capitalized >= len(words) * 0.7:
                # Check if it's not a common word
                common_words = {'GOVERNMENT', 'INDIA', 'AADHAAR', 'UIDAI', 'YEAR', 'BIRTH'}
                if not any(word.upper() in common_words for word in words):
                    candidate_names.append((line, len(line)))
    
    if candidate_names:
        # Get longest candidate (usually the name)
        result['name'] = max(candidate_names, key=lambda x: x[1])[0]
    
    return result


def extract_aadhaar_back_fields(ocr_text):
    """
    Extract Aadhaar back (address) fields from OCR text
    
    Args:
        ocr_text: Combined OCR text string
        
    Returns:
        Dictionary with extracted address
    """
    result = {
        'address': None
    }
    
    # Common header/footer text to exclude
    exclude_keywords = [
        'government', 'india', 'uidai', 'aadhaar', 'information',
        'establish', 'identity', 'authenticate', 'online', 'valid',
        'throughout', 'country', 'enrolment', 'update', 'download',
        'your', 'address', 'date', 'year', 'birth', 'gender'
    ]
    
    # Address indicators
    address_indicators = [
        'road', 'street', 'lane', 'nagar', 'colony', 'society', 'chs', 'building', 
        'near', 'opposite', 'behind', 'hospital', 'school', 'market', 'chowk'
    ]
    
    lines = ocr_text.split('\n')
    address_lines = []
    skip_until_address = True  # Skip header text until we find actual address
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        line_lower = line.lower()
        
        # Skip lines that are clearly header/footer
        if any(keyword in line_lower for keyword in exclude_keywords):
            continue
        
        # Skip lines with too many special characters (OCR garbage)
        special_char_count = sum(1 for c in line if c in '|[]{}()&@#$%^*+=_~`')
        if len(line) > 0 and special_char_count / len(line) > 0.3:  # More than 30% special chars
            continue
        
        # Skip very short lines with mostly special chars
        if len(line) < 5 and special_char_count > 2:
            continue
        
        # Skip lines that are all uppercase and very long (likely headers)
        if line.isupper() and len(line) > 40:
            continue
        
        # Look for address indicators
        has_address_indicator = any(indicator in line_lower for indicator in address_indicators)
        has_pin = re.search(r'\b\d{6}\b', line)  # PIN code (6 digits)
        has_number = re.search(r'\b\d+\b', line)  # Street/house number
        has_city_state = re.search(r'\b(mumbai|delhi|bangalore|chennai|kolkata|pune|hyderabad|maharashtra|karnataka|tamil|nadu|west bengal|gujarat|rajasthan|uttar pradesh|bihar|madhya pradesh|andhra pradesh|telangana|odisha|assam|jammu|kashmir|punjab|haryana|himachal|uttarakhand|goa|kerala|manipur|meghalaya|mizoram|nagaland|sikkim|tripura|arunachal|dahisar|andheri|borivali|kandivali|malad|jogeshwari|goregaon|bandra|khar|santacruz|vile parle|juhu|versova|andheri west|andheri east|powai|bhandup|mulund|thane|kalyan|dombivli|ulhasnagar|ambernath|badlapur|vasai|virar|nalasopara|mira|bhayandar)\b', line_lower)
        
        # Check if this looks like an address line
        is_address_line = False
        
        # If we find PIN code, this is definitely address
        if has_pin:
            is_address_line = True
            skip_until_address = False
        
        # If we find address indicator with number or reasonable length
        if has_address_indicator and (has_number or len(line) > 15):
            is_address_line = True
            skip_until_address = False
        
        # If we find city/state name, likely address
        if has_city_state:
            is_address_line = True
            skip_until_address = False
        
        # If we have number and reasonable length (house/building number)
        if has_number and len(line) > 10 and not skip_until_address:
            # Check it's not just random numbers
            if re.search(r'[a-zA-Z]', line):  # Has letters too
                is_address_line = True
        
        # If we're past the header section and line looks reasonable
        if not skip_until_address and len(line) > 8 and special_char_count / len(line) < 0.2:
            # Check if it contains common address words or patterns
            if re.search(r'\b\d+[a-zA-Z]?\b', line) or re.search(r'[a-zA-Z]+\s+[a-zA-Z]+', line):
                is_address_line = True
        
        if is_address_line:
            # Clean up the line: remove excessive special chars at start/end
            cleaned_line = re.sub(r'^[|\[\]{}()&@#$%^*+=_~`\s]+', '', line)
            cleaned_line = re.sub(r'[|\[\]{}()&@#$%^*+=_~`\s]+$', '', cleaned_line)
            if cleaned_line:
                address_lines.append(cleaned_line)
    
    if address_lines:
        # Join and clean up the address
        address = '\n'.join(address_lines)
        # Remove excessive newlines
        address = re.sub(r'\n{3,}', '\n\n', address)
        # Remove lines that are too short and likely OCR errors
        final_lines = []
        for line in address.split('\n'):
            line = line.strip()
            if len(line) >= 5 or re.search(r'\d{6}', line):  # Keep if reasonable length or has PIN
                final_lines.append(line)
        
        if final_lines:
            result['address'] = '\n'.join(final_lines)
    
    return result


class KYCDocumentOCRView(APIView):
    """
    KYC Document OCR API
    Extracts structured data from PAN and Aadhaar documents
    """
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Process KYC document and extract fields
        
        Request:
        - document_type: PAN, AADHAAR_FRONT, AADHAAR_BACK, OTHER
        - document_image: image file (jpg/png/jpeg)
        
        Response:
        {
            "success": true,
            "data": {
                "pan_number": "...",
                "dob": "...",
                "name": "...",
                ...
            }
        }
        """
        try:
            # Get document type
            document_type = request.data.get('document_type', '').upper()
            
            if document_type not in ['PAN', 'AADHAAR_FRONT', 'AADHAAR_BACK', 'OTHER']:
                return Response({
                    'success': False,
                    'message': f'Invalid document_type. Must be one of: PAN, AADHAAR_FRONT, AADHAAR_BACK, OTHER'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get image file
            image_file = request.FILES.get('document_image')
            if not image_file:
                return Response({
                    'success': False,
                    'message': 'document_image file is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate file type
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
            file_name = image_file.name.lower()
            if not any(file_name.endswith(ext.lower()) for ext in allowed_extensions):
                return Response({
                    'success': False,
                    'message': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Preprocess image
            try:
                processed_image = preprocess_image(image_file)
            except Exception as e:
                logger.error(f"Image preprocessing failed: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Image preprocessing failed: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Run OCR - try PaddleOCR first, then EasyOCR, then Tesseract as final fallback
            # Or skip PyTorch-based OCRs if SKIP_PYTORCH_OCR is True
            ocr_text = None
            last_error = None
            
            if SKIP_PYTORCH_OCR:
                # Skip PaddleOCR and EasyOCR, use Tesseract directly
                logger.info("Skipping PyTorch-based OCRs (PaddleOCR/EasyOCR), using Tesseract directly...")
                try:
                    ocr_text = extract_text_from_tesseract(processed_image)
                    logger.info("Successfully used Tesseract OCR")
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Tesseract OCR failed: {error_msg}")
                    return Response({
                        'success': False,
                        'message': error_msg  # Error message already contains installation instructions
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Try PaddleOCR first
                try:
                    ocr = get_paddle_ocr()
                    ocr_result = ocr.ocr(processed_image)
                    ocr_text = extract_text_from_paddleocr(ocr_result)
                    logger.info("Successfully used PaddleOCR")
                except Exception as e:
                    error_msg = str(e)
                    last_error = f"PaddleOCR: {error_msg}"
                    logger.warning(f"PaddleOCR failed: {error_msg}. Trying EasyOCR fallback...")
                    
                    # Try EasyOCR as fallback
                    try:
                        easy_ocr = get_easy_ocr()
                        ocr_result_easy = easy_ocr.readtext(processed_image)
                        ocr_text = extract_text_from_easyocr(ocr_result_easy)
                        logger.info("Successfully used EasyOCR as fallback")
                    except Exception as e2:
                        error_msg2 = str(e2)
                        last_error = f"{last_error}; EasyOCR: {error_msg2}"
                        logger.warning(f"EasyOCR also failed: {error_msg2}. Trying Tesseract OCR as final fallback...")
                        
                        # Try Tesseract OCR as final fallback (no PyTorch dependency)
                        try:
                            ocr_text = extract_text_from_tesseract(processed_image)
                            logger.info("Successfully used Tesseract OCR as final fallback")
                        except Exception as e3:
                            error_msg3 = str(e3)
                            last_error = f"{last_error}; Tesseract: {error_msg3}"
                            logger.error(f"All OCR libraries failed. {last_error}")
                            return Response({
                                'success': False,
                                'message': (
                                    f'All OCR libraries failed. Errors: {last_error}\n\n'
                                    'Quick Fix: Install Tesseract OCR (no PyTorch dependency):\n'
                                    '1. Download: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.4.0.20240605.exe\n'
                                    '2. Install and check "Add to PATH"\n'
                                    '3. Restart server\n'
                                    'Or set SKIP_PYTORCH_OCR = True in kyc_ocr_views.py to use only Tesseract'
                                )
                            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Validate OCR text
            if not ocr_text or not ocr_text.strip():
                return Response({
                    'success': False,
                    'message': 'No text detected in image. Please ensure the document is clear and readable.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if debug mode (return raw OCR text)
            debug_mode = request.query_params.get('debug', 'false').lower() == 'true'
            
            # Extract fields based on document type
            extracted_data = {}
            
            if document_type == 'PAN':
                extracted_data = extract_pan_fields(ocr_text)
            elif document_type == 'AADHAAR_FRONT':
                extracted_data = extract_aadhaar_front_fields(ocr_text)
            elif document_type == 'AADHAAR_BACK':
                extracted_data = extract_aadhaar_back_fields(ocr_text)
            else:  # OTHER
                # For other documents, return raw OCR text
                extracted_data = {
                    'raw_text': ocr_text,
                    'lines': ocr_text.split('\n')
                }
            
            # Add raw OCR text in debug mode
            response_data = {
                'success': True,
                'message': 'Document processed successfully',
                'data': extracted_data,
                'metadata': {
                    'document_type': document_type,
                    'ocr_text_length': len(ocr_text),
                    'processed_at': str(timezone.now())
                }
            }
            
            if debug_mode:
                response_data['debug'] = {
                    'raw_ocr_text': ocr_text,
                    'ocr_lines': ocr_text.split('\n')
                }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"KYC OCR processing error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': f'Processing failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

