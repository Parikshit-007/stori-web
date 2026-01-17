"""
Example usage of the Face Matching System
This script demonstrates how to use the face matching module
"""

from face_match import (
    FaceMatcher,
    MultiModelFaceMatcher,
    verify_identity_documents,
    FaceMatchConfig
)
import json


def example_1_basic_verification():
    """Example 1: Basic face verification between two images"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Face Verification")
    print("="*60)
    
    # Initialize the face matcher with high accuracy settings
    matcher = FaceMatcher(
        model_name='Facenet512',      # High accuracy model
        detector_backend='retinaface', # Best face detection
        distance_metric='cosine'
    )
    
    # Verify user photo against Aadhaar
    # Replace these paths with your actual image paths
    user_photo = 'path/to/user_selfie.jpg'
    aadhaar_photo = 'path/to/aadhaar_image.jpg'
    
    try:
        result = matcher.verify_faces(
            user_image=user_photo,
            document_image=aadhaar_photo,
            document_type='Aadhaar'
        )
        
        print(f"\n✓ Verification Result:")
        print(f"  - Match: {result.is_match}")
        print(f"  - Confidence: {result.confidence:.2f}%")
        print(f"  - Match Strength: {result._get_match_strength()}")
        print(f"  - Distance: {result.distance:.4f}")
        print(f"  - Threshold: {result.threshold:.4f}")
        print(f"\nFull Result:")
        print(json.dumps(result.to_dict(), indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")


def example_2_multiple_documents():
    """Example 2: Verify against multiple documents (Aadhaar, PAN, Voter ID)"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Multiple Documents Verification")
    print("="*60)
    
    matcher = FaceMatcher(
        model_name='Facenet512',
        detector_backend='retinaface'
    )
    
    # User photo
    user_photo = 'path/to/user_selfie.jpg'
    
    # All identity documents
    documents = {
        'Aadhaar': 'path/to/aadhaar.jpg',
        'PAN': 'path/to/pan.jpg',
        'Voter_ID': 'path/to/voter_id.jpg'
    }
    
    try:
        # Get comprehensive report
        report = matcher.get_detailed_verification_report(
            user_image=user_photo,
            documents=documents
        )
        
        print(f"\n✓ Verification Report:")
        print(f"  - Overall Verdict: {report['overall_verdict']}")
        print(f"  - Description: {report['verdict_description']}")
        print(f"  - Successful Matches: {report['successful_matches']}/{report['total_documents']}")
        print(f"  - Average Confidence: {report['average_confidence']:.2f}%")
        
        print(f"\n  Individual Results:")
        for doc_type, result in report['individual_results'].items():
            if result:
                print(f"    • {doc_type}:")
                print(f"      - Match: {result['is_match']}")
                print(f"      - Confidence: {result['confidence']:.2f}%")
                print(f"      - Match Strength: {result['match_strength']}")
        
        print(f"\nFull Report:")
        print(json.dumps(report, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")


def example_3_multi_model_consensus():
    """Example 3: Use multiple models for highest accuracy (consensus-based)"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Multi-Model Consensus (Highest Accuracy)")
    print("="*60)
    
    # Initialize multi-model matcher with top 3 models
    multi_matcher = MultiModelFaceMatcher(
        models=['Facenet512', 'ArcFace', 'VGG-Face'],
        detector_backend='retinaface',
        consensus_threshold=0.6  # 60% of models must agree
    )
    
    user_photo = 'path/to/user_selfie.jpg'
    aadhaar_photo = 'path/to/aadhaar.jpg'
    
    try:
        result = multi_matcher.verify_faces_consensus(
            user_image=user_photo,
            document_image=aadhaar_photo,
            document_type='Aadhaar'
        )
        
        print(f"\n✓ Consensus Result:")
        print(f"  - Match: {result['is_match']}")
        print(f"  - Confidence: {result['confidence']:.2f}%")
        print(f"  - Models Agreed: {result['models_agreed']}/{result['total_models']}")
        print(f"  - Match Ratio: {result['match_ratio']:.2f}")
        print(f"  - Consensus Strength: {result['consensus_strength']}")
        
        print(f"\n  Individual Model Results:")
        for idx, model_result in enumerate(result['individual_results'], 1):
            print(f"    {idx}. {model_result['model_used']}:")
            print(f"       - Match: {model_result['is_match']}")
            print(f"       - Confidence: {model_result['confidence']:.2f}%")
        
        print(f"\nFull Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")


def example_4_convenience_function():
    """Example 4: Using the convenience function for quick verification"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Convenience Function (Easiest Method)")
    print("="*60)
    
    try:
        # One-line verification of all documents
        report = verify_identity_documents(
            user_photo_path='path/to/user_selfie.jpg',
            aadhaar_image='path/to/aadhaar.jpg',
            pan_image='path/to/pan.jpg',
            voter_id_image='path/to/voter_id.jpg',
            use_multi_model=False  # Set to True for highest accuracy
        )
        
        print(f"\n✓ Quick Verification Result:")
        print(json.dumps(report, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")


def example_5_api_integration():
    """Example 5: Integration with API (base64 encoded images)"""
    print("\n" + "="*60)
    print("EXAMPLE 5: API Integration (Base64 Images)")
    print("="*60)
    
    matcher = FaceMatcher(
        model_name='Facenet512',
        detector_backend='retinaface'
    )
    
    # Simulate receiving base64 images from API
    # In real scenario, you would receive these from API request
    
    """
    Example API payload:
    {
        "user_image_base64": "iVBORw0KGgoAAAANS...",
        "aadhaar_image_base64": "iVBORw0KGgoAAAANS...",
        "pan_image_base64": "iVBORw0KGgoAAAANS...",
        "voter_id_image_base64": "iVBORw0KGgoAAAANS..."
    }
    """
    
    # Example: Load image and convert to base64
    import base64
    
    def image_to_base64(image_path):
        """Helper function to convert image to base64"""
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    try:
        # Convert images to base64 (simulating API input)
        user_image_b64 = image_to_base64('path/to/user_selfie.jpg')
        aadhaar_image_b64 = image_to_base64('path/to/aadhaar.jpg')
        
        # Verify using base64 strings
        result = matcher.verify_faces(
            user_image=user_image_b64,
            document_image=aadhaar_image_b64,
            document_type='Aadhaar'
        )
        
        print(f"\n✓ API Verification Result:")
        print(f"  - Match: {result.is_match}")
        print(f"  - Confidence: {result.confidence:.2f}%")
        
        # Response format for API
        api_response = {
            'success': True,
            'verification': result.to_dict()
        }
        
        print(f"\nAPI Response:")
        print(json.dumps(api_response, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")


def example_6_different_models_comparison():
    """Example 6: Compare different models"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Model Comparison")
    print("="*60)
    
    user_photo = 'path/to/user_selfie.jpg'
    aadhaar_photo = 'path/to/aadhaar.jpg'
    
    # Test different models
    models_to_test = ['VGG-Face', 'Facenet', 'Facenet512', 'ArcFace']
    
    print(f"\nComparing {len(models_to_test)} models:")
    results = []
    
    for model_name in models_to_test:
        try:
            matcher = FaceMatcher(
                model_name=model_name,
                detector_backend='retinaface'
            )
            
            result = matcher.verify_faces(
                user_image=user_photo,
                document_image=aadhaar_photo,
                document_type='Aadhaar'
            )
            
            results.append({
                'model': model_name,
                'match': result.is_match,
                'confidence': result.confidence,
                'distance': result.distance
            })
            
            print(f"\n  • {model_name}:")
            print(f"    - Match: {result.is_match}")
            print(f"    - Confidence: {result.confidence:.2f}%")
            print(f"    - Distance: {result.distance:.4f}")
            
        except Exception as e:
            print(f"  • {model_name}: Error - {str(e)}")
    
    # Summary
    if results:
        matches = sum(1 for r in results if r['match'])
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        
        print(f"\n  Summary:")
        print(f"    - Models agreeing: {matches}/{len(results)}")
        print(f"    - Average confidence: {avg_confidence:.2f}%")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" FACE MATCHING SYSTEM - USAGE EXAMPLES")
    print("="*70)
    print("\nNote: Replace 'path/to/...' with actual image paths to run examples")
    print("="*70)
    
    # Uncomment the examples you want to run
    
    # example_1_basic_verification()
    # example_2_multiple_documents()
    # example_3_multi_model_consensus()
    # example_4_convenience_function()
    # example_5_api_integration()
    # example_6_different_models_comparison()
    
    print("\n" + "="*70)
    print(" To run examples, uncomment the function calls in main()")
    print(" and replace image paths with your actual file paths")
    print("="*70)


if __name__ == "__main__":
    main()

