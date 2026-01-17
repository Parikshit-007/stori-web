"""
Test script to verify Face Matching System installation
Run this after installing dependencies
"""

import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    print("-" * 60)
    
    dependencies = {
        'deepface': 'DeepFace',
        'tensorflow': 'TensorFlow',
        'cv2': 'OpenCV',
        'PIL': 'Pillow',
        'numpy': 'NumPy'
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} - OK")
        except ImportError:
            print(f"✗ {name} - MISSING")
            missing.append(name)
    
    print("-" * 60)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("\nInstall missing dependencies with:")
        print("pip install -r face_match_requirements.txt")
        return False
    else:
        print("\n✓ All dependencies installed successfully!")
        return True


def test_face_match_import():
    """Test if face_match module can be imported"""
    print("\n\nTesting face_match module import...")
    print("-" * 60)
    
    try:
        from face_match import (
            FaceMatcher,
            MultiModelFaceMatcher,
            FaceMatchConfig,
            FaceMatchResult,
            verify_identity_documents
        )
        print("✓ FaceMatcher - OK")
        print("✓ MultiModelFaceMatcher - OK")
        print("✓ FaceMatchConfig - OK")
        print("✓ FaceMatchResult - OK")
        print("✓ verify_identity_documents - OK")
        print("-" * 60)
        print("\n✓ Face matching module imported successfully!")
        return True
    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        print("-" * 60)
        return False


def test_model_initialization():
    """Test if models can be initialized"""
    print("\n\nTesting model initialization...")
    print("-" * 60)
    
    try:
        from face_match import FaceMatcher
        
        print("Initializing FaceMatcher (this may take a moment)...")
        matcher = FaceMatcher(
            model_name='Facenet512',
            detector_backend='retinaface'
        )
        print("✓ FaceMatcher initialized successfully!")
        
        print("\nAvailable models:", FaceMatcher.__module__)
        print("-" * 60)
        print("\n✓ Model initialization test passed!")
        return True
    except Exception as e:
        print(f"✗ Model initialization failed: {str(e)}")
        print("\nNote: Models will be downloaded on first use.")
        print("This requires internet connection and may take a few minutes.")
        print("-" * 60)
        return False


def test_with_sample_images():
    """Test with sample images if available"""
    print("\n\nTesting with sample images...")
    print("-" * 60)
    
    # Check if sample images exist
    sample_dir = os.path.join(os.path.dirname(__file__), 'sample_images')
    
    if not os.path.exists(sample_dir):
        print("ℹ Sample images not found (optional)")
        print(f"  Create folder: {sample_dir}")
        print("  Add test images: user_photo.jpg, aadhaar.jpg")
        print("-" * 60)
        return None
    
    user_photo = os.path.join(sample_dir, 'user_photo.jpg')
    aadhaar_photo = os.path.join(sample_dir, 'aadhaar.jpg')
    
    if not (os.path.exists(user_photo) and os.path.exists(aadhaar_photo)):
        print("ℹ Sample images not complete (optional)")
        print("  Add: user_photo.jpg and aadhaar.jpg to sample_images/")
        print("-" * 60)
        return None
    
    try:
        from face_match import FaceMatcher
        
        print("Running face verification on sample images...")
        matcher = FaceMatcher()
        
        result = matcher.verify_faces(
            user_image=user_photo,
            document_image=aadhaar_photo,
            document_type='Aadhaar'
        )
        
        print(f"\n✓ Verification completed!")
        print(f"  - Match: {result.is_match}")
        print(f"  - Confidence: {result.confidence:.2f}%")
        print(f"  - Match Strength: {result._get_match_strength()}")
        print("-" * 60)
        print("\n✓ Sample image test passed!")
        return True
    except Exception as e:
        print(f"✗ Sample image test failed: {str(e)}")
        print("-" * 60)
        return False


def show_usage_example():
    """Show a quick usage example"""
    print("\n\n" + "="*60)
    print("QUICK USAGE EXAMPLE")
    print("="*60)
    
    example_code = """
# Basic face verification
from face_match import FaceMatcher

# Initialize matcher
matcher = FaceMatcher(
    model_name='Facenet512',
    detector_backend='retinaface'
)

# Verify faces
result = matcher.verify_faces(
    user_image='path/to/user_photo.jpg',
    document_image='path/to/aadhaar.jpg',
    document_type='Aadhaar'
)

print(f"Match: {result.is_match}")
print(f"Confidence: {result.confidence}%")
print(f"Match Strength: {result._get_match_strength()}")

# Multiple documents
documents = {
    'Aadhaar': 'path/to/aadhaar.jpg',
    'PAN': 'path/to/pan.jpg',
    'Voter_ID': 'path/to/voter_id.jpg'
}

report = matcher.get_detailed_verification_report(
    user_image='path/to/user_photo.jpg',
    documents=documents
)

print(f"Overall Verdict: {report['overall_verdict']}")
print(f"Matches: {report['successful_matches']}/{report['total_documents']}")
"""
    
    print(example_code)
    print("="*60)
    print("\nFor more examples, see: face_match_example.py")
    print("For documentation, see: FACE_MATCH_README.md")
    print("="*60)


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(" FACE MATCHING SYSTEM - INSTALLATION TEST")
    print("="*60)
    
    # Test 1: Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n⚠ Please install dependencies first!")
        sys.exit(1)
    
    # Test 2: Test module import
    import_ok = test_face_match_import()
    if not import_ok:
        print("\n⚠ Module import failed!")
        sys.exit(1)
    
    # Test 3: Test model initialization (optional)
    print("\n⚠ Model initialization test (optional, requires download)")
    response = input("Do you want to test model initialization? (y/n): ")
    if response.lower() == 'y':
        test_model_initialization()
    
    # Test 4: Test with sample images (optional)
    test_with_sample_images()
    
    # Show usage example
    show_usage_example()
    
    print("\n" + "="*60)
    print(" ✓ INSTALLATION TEST COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. See face_match_example.py for usage examples")
    print("2. Read FACE_MATCH_README.md for documentation")
    print("3. Start using face_match.py in your application")
    print("="*60)


if __name__ == "__main__":
    main()


