# Face Matching System - High Accuracy Identity Verification

A comprehensive face matching solution for verifying user photos against identity documents (Aadhaar, PAN, Voter ID) with state-of-the-art accuracy.

## Features

✅ **High Accuracy**: Uses state-of-the-art deep learning models (Facenet512, ArcFace, VGG-Face)  
✅ **Multiple Document Support**: Aadhaar, PAN, Voter ID, and more  
✅ **Multi-Model Consensus**: Combine multiple models for highest accuracy  
✅ **Flexible Input**: Supports file paths, base64 strings, bytes, and numpy arrays  
✅ **API Ready**: Easy integration with REST APIs  
✅ **Detailed Reports**: Comprehensive verification reports with confidence scores  
✅ **Robust Detection**: Multiple face detection backends (RetinaFace, MTCNN, etc.)  

## Installation

### 1. Install Dependencies

```bash
pip install -r face_match_requirements.txt
```

Or install manually:

```bash
pip install deepface tensorflow opencv-python Pillow numpy mtcnn retina-face
```

### 2. Download Models (First Run)

The first time you run the face matcher, it will automatically download the required models (this may take a few minutes).

## Quick Start

### Basic Usage (Single Document)

```python
from face_match import FaceMatcher

# Initialize matcher
matcher = FaceMatcher(
    model_name='Facenet512',      # High accuracy model
    detector_backend='retinaface'  # Best face detection
)

# Verify face
result = matcher.verify_faces(
    user_image='user_photo.jpg',
    document_image='aadhaar.jpg',
    document_type='Aadhaar'
)

print(f"Match: {result.is_match}")
print(f"Confidence: {result.confidence}%")
print(f"Match Strength: {result._get_match_strength()}")
```

### Multiple Documents Verification

```python
from face_match import FaceMatcher

matcher = FaceMatcher()

documents = {
    'Aadhaar': 'aadhaar.jpg',
    'PAN': 'pan.jpg',
    'Voter_ID': 'voter_id.jpg'
}

report = matcher.get_detailed_verification_report(
    user_image='user_photo.jpg',
    documents=documents
)

print(f"Overall Verdict: {report['overall_verdict']}")
print(f"Successful Matches: {report['successful_matches']}/{report['total_documents']}")
print(f"Average Confidence: {report['average_confidence']}%")
```

### Highest Accuracy (Multi-Model Consensus)

```python
from face_match import MultiModelFaceMatcher

# Use multiple models for consensus-based verification
matcher = MultiModelFaceMatcher(
    models=['Facenet512', 'ArcFace', 'VGG-Face'],
    consensus_threshold=0.6  # 60% of models must agree
)

result = matcher.verify_faces_consensus(
    user_image='user_photo.jpg',
    document_image='aadhaar.jpg',
    document_type='Aadhaar'
)

print(f"Consensus Match: {result['is_match']}")
print(f"Models Agreed: {result['models_agreed']}/{result['total_models']}")
print(f"Confidence: {result['confidence']}%")
```

### Convenience Function (Easiest)

```python
from face_match import verify_identity_documents

report = verify_identity_documents(
    user_photo_path='user_photo.jpg',
    aadhaar_image='aadhaar.jpg',
    pan_image='pan.jpg',
    voter_id_image='voter_id.jpg',
    use_multi_model=True  # For highest accuracy
)

print(report)
```

## API Integration

### Using Base64 Encoded Images

```python
from face_match import FaceMatcher
import base64

matcher = FaceMatcher()

# Receive base64 from API
user_image_base64 = "iVBORw0KGgoAAAANS..."  # From API request
document_image_base64 = "iVBORw0KGgoAAAANS..."

# Verify
result = matcher.verify_faces(
    user_image=user_image_base64,
    document_image=document_image_base64,
    document_type='Aadhaar'
)

# API response
api_response = {
    'success': True,
    'verification': result.to_dict()
}
```

### Flask API Example

```python
from flask import Flask, request, jsonify
from face_match import FaceMatcher
import base64

app = Flask(__name__)
matcher = FaceMatcher(model_name='Facenet512', detector_backend='retinaface')

@app.route('/verify-face', methods=['POST'])
def verify_face():
    data = request.json
    
    try:
        result = matcher.verify_faces(
            user_image=data['user_image_base64'],
            document_image=data['document_image_base64'],
            document_type=data.get('document_type', 'Unknown')
        )
        
        return jsonify({
            'success': True,
            'is_match': result.is_match,
            'confidence': result.confidence,
            'match_strength': result._get_match_strength(),
            'details': result.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/verify-multiple', methods=['POST'])
def verify_multiple():
    data = request.json
    
    documents = {}
    if 'aadhaar_image' in data:
        documents['Aadhaar'] = data['aadhaar_image']
    if 'pan_image' in data:
        documents['PAN'] = data['pan_image']
    if 'voter_id_image' in data:
        documents['Voter_ID'] = data['voter_id_image']
    
    try:
        report = matcher.get_detailed_verification_report(
            user_image=data['user_image'],
            documents=documents
        )
        
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
```

## Model Options

### Available Models (Ordered by Accuracy)

| Model | Accuracy | Speed | Best For |
|-------|----------|-------|----------|
| **ArcFace** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | Highest accuracy |
| **Facenet512** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | Best balance (Recommended) |
| **VGG-Face** | ⭐⭐⭐⭐ | ⚡⚡ | Good accuracy |
| **Facenet** | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | Fast and accurate |
| **DeepFace** | ⭐⭐⭐ | ⚡⚡ | Original DeepFace |
| **OpenFace** | ⭐⭐⭐ | ⚡⚡⚡⚡⚡ | Lightweight |

### Face Detection Backends

| Backend | Accuracy | Speed | Best For |
|---------|----------|-------|----------|
| **retinaface** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | Best detection (Recommended) |
| **mtcnn** | ⭐⭐⭐⭐ | ⚡⚡⚡ | Good balance |
| **ssd** | ⭐⭐⭐ | ⚡⚡⚡⚡ | Fast detection |
| **opencv** | ⭐⭐ | ⚡⚡⚡⚡⚡ | Fastest |
| **dlib** | ⭐⭐⭐ | ⚡⚡ | Traditional |

## Configuration Options

### FaceMatcher Parameters

```python
matcher = FaceMatcher(
    model_name='Facenet512',       # Model to use
    detector_backend='retinaface', # Face detection backend
    distance_metric='cosine',      # 'cosine', 'euclidean', 'euclidean_l2'
    enforce_detection=True         # Raise error if no face detected
)
```

### MultiModelFaceMatcher Parameters

```python
multi_matcher = MultiModelFaceMatcher(
    models=['Facenet512', 'ArcFace', 'VGG-Face'],  # Models to use
    detector_backend='retinaface',                  # Face detection
    consensus_threshold=0.6                         # 60% must agree (0.0-1.0)
)
```

## Understanding Results

### FaceMatchResult Object

```python
result = matcher.verify_faces(user_image, document_image, 'Aadhaar')

# Properties
result.is_match          # True/False
result.confidence        # 0-100 (higher is better)
result.distance          # Distance metric (lower is more similar)
result.threshold         # Model's threshold
result.model_used        # Model name used
result.document_type     # Document type

# Methods
result.to_dict()         # Convert to dictionary
result._get_match_strength()  # "Very Strong Match", "Strong Match", etc.
```

### Match Strength Interpretation

| Confidence | Match Strength | Interpretation |
|------------|----------------|----------------|
| 95-100% | Very Strong Match | Highly confident match |
| 85-94% | Strong Match | Good match |
| 75-84% | Good Match | Acceptable match |
| 65-74% | Moderate Match | Borderline match |
| < 65% | Weak Match | Unreliable match |

### Overall Verdict

- **VERIFIED**: All documents match successfully
- **PARTIALLY_VERIFIED**: Some documents match
- **NOT_VERIFIED**: No matching documents

## Best Practices

### 1. Image Quality

✅ **Good Images:**
- Clear, well-lit photos
- Face is clearly visible
- Minimal blur
- Frontal face view
- Resolution: 640x480 or higher

❌ **Poor Images:**
- Dark or overexposed
- Blurry or out of focus
- Face partially covered
- Extreme angles
- Very low resolution

### 2. Model Selection

- **For Production**: Use `Facenet512` or `ArcFace` with `retinaface` backend
- **For Speed**: Use `Facenet` with `mtcnn` backend
- **For Highest Accuracy**: Use `MultiModelFaceMatcher` with consensus

### 3. Security Considerations

- Validate image file types and sizes
- Implement rate limiting for API
- Store verification logs for audit
- Use HTTPS for API communication
- Don't store biometric data without consent

### 4. Error Handling

```python
from face_match import FaceMatcher

matcher = FaceMatcher()

try:
    result = matcher.verify_faces(user_image, document_image, 'Aadhaar')
    
    if result.is_match and result.confidence >= 85:
        # High confidence match - proceed
        print("Identity verified!")
    elif result.is_match and result.confidence >= 70:
        # Moderate confidence - may need manual review
        print("Manual review recommended")
    else:
        # No match or low confidence
        print("Verification failed")
        
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Verification error: {e}")
```

## Performance Optimization

### 1. Preload Models

```python
# Initialize once (e.g., at app startup)
matcher = FaceMatcher(model_name='Facenet512', detector_backend='retinaface')

# Reuse for multiple verifications
for user_image, doc_image in image_pairs:
    result = matcher.verify_faces(user_image, doc_image, 'Aadhaar')
```

### 2. Batch Processing

```python
# Process multiple documents in parallel
from concurrent.futures import ThreadPoolExecutor

def verify_document(doc_type, doc_image):
    return matcher.verify_faces(user_image, doc_image, doc_type)

documents = {'Aadhaar': 'aadhaar.jpg', 'PAN': 'pan.jpg', 'Voter_ID': 'voter.jpg'}

with ThreadPoolExecutor() as executor:
    results = dict(executor.map(
        lambda item: (item[0], verify_document(*item)),
        documents.items()
    ))
```

### 3. Image Preprocessing

Images are automatically preprocessed, but you can optimize by:
- Resizing large images before verification
- Converting to RGB format
- Ensuring proper orientation

## Troubleshooting

### Common Issues

**Issue: "No face detected in the image"**
- Ensure face is clearly visible
- Try different detector backend (`mtcnn` or `ssd`)
- Check image quality and lighting
- Set `enforce_detection=False` for lenient detection

**Issue: "Model download failed"**
- Check internet connection
- Models are downloaded on first use
- Requires ~100-500MB for models

**Issue: "Low confidence scores"**
- Verify image quality
- Ensure same person in both images
- Try multi-model consensus for better accuracy
- Check if face angles are similar

**Issue: "Slow performance"**
- Use faster model (`Facenet` instead of `ArcFace`)
- Use faster backend (`mtcnn` or `ssd`)
- Preload models at startup
- Resize images before processing

## Examples

See `face_match_example.py` for comprehensive examples including:
- Basic verification
- Multiple documents
- Multi-model consensus
- API integration
- Model comparison

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **GPU**: Optional (significantly faster with CUDA-enabled GPU)
- **Disk Space**: ~2GB for models

## License & Credits

This module uses:
- **DeepFace**: https://github.com/serengil/deepface
- **TensorFlow**: https://www.tensorflow.org/
- **OpenCV**: https://opencv.org/

## Support

For issues or questions:
1. Check the examples in `face_match_example.py`
2. Review this documentation
3. Check DeepFace documentation: https://github.com/serengil/deepface

## Version History

- **v1.0.0**: Initial release with multi-model support

---

**Note**: Always comply with local privacy laws and regulations when processing biometric data.


