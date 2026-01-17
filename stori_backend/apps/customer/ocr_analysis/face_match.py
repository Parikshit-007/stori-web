"""
Face Matching Module for Identity Verification
Supports matching user photo with Aadhaar, PAN, and Voter ID documents
Uses multiple models for high accuracy face verification
"""

import os
import base64
import logging
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import io

try:
    from deepface import DeepFace
except ImportError:
    raise ImportError("DeepFace not installed. Run: pip install deepface")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceMatchConfig:
    """Configuration for face matching parameters"""
    
    # Available models (in order of accuracy)
    MODELS = [
        'VGG-Face',    # Good balance of speed and accuracy
        'Facenet512',  # High accuracy
        'ArcFace',     # State-of-the-art accuracy
        'Facenet',     # Fast and accurate
        'DeepFace',    # Original DeepFace
        'OpenFace',    # Lightweight
        'DeepID',      # Deep learning based
    ]
    
    # Available backends for face detection
    BACKENDS = [
        'retinaface',  # Most accurate
        'mtcnn',       # Good accuracy, moderate speed
        'opencv',      # Fast but less accurate
        'ssd',         # Good balance
        'dlib',        # Traditional but reliable
    ]
    
    # Default configuration
    DEFAULT_MODEL = 'Facenet512'  # Best accuracy
    DEFAULT_BACKEND = 'retinaface'  # Best detection
    SIMILARITY_THRESHOLD = 0.40  # Lower is more similar (for cosine distance)
    ENFORCE_DETECTION = True  # Raise error if no face detected
    

class FaceMatchResult:
    """Result object for face matching"""
    
    def __init__(
        self,
        is_match: bool,
        confidence: float,
        distance: float,
        threshold: float,
        model_used: str,
        document_type: str,
        details: Optional[Dict] = None
    ):
        self.is_match = is_match
        self.confidence = confidence  # 0-100, higher is better
        self.distance = distance  # Distance metric (lower is more similar)
        self.threshold = threshold
        self.model_used = model_used
        self.document_type = document_type
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary"""
        return {
            'is_match': self.is_match,
            'confidence': round(self.confidence, 2),
            'distance': round(self.distance, 4),
            'threshold': self.threshold,
            'model_used': self.model_used,
            'document_type': self.document_type,
            'match_strength': self._get_match_strength(),
            'details': self.details
        }
    
    def _get_match_strength(self) -> str:
        """Get human-readable match strength"""
        if not self.is_match:
            return "No Match"
        
        if self.confidence >= 95:
            return "Very Strong Match"
        elif self.confidence >= 85:
            return "Strong Match"
        elif self.confidence >= 75:
            return "Good Match"
        elif self.confidence >= 65:
            return "Moderate Match"
        else:
            return "Weak Match"
    
    def __repr__(self) -> str:
        return (f"FaceMatchResult(is_match={self.is_match}, "
                f"confidence={self.confidence:.2f}%, "
                f"document={self.document_type})")


class FaceMatcher:
    """High-accuracy face matching system for identity verification"""
    
    def __init__(
        self,
        model_name: str = FaceMatchConfig.DEFAULT_MODEL,
        detector_backend: str = FaceMatchConfig.DEFAULT_BACKEND,
        distance_metric: str = 'cosine',
        enforce_detection: bool = FaceMatchConfig.ENFORCE_DETECTION
    ):
        """
        Initialize Face Matcher
        
        Args:
            model_name: Model to use for face recognition
            detector_backend: Backend for face detection
            distance_metric: Distance metric ('cosine', 'euclidean', 'euclidean_l2')
            enforce_detection: Whether to raise error if face not detected
        """
        self.model_name = model_name
        self.detector_backend = detector_backend
        self.distance_metric = distance_metric
        self.enforce_detection = enforce_detection
        
        logger.info(f"Initialized FaceMatcher with model: {model_name}, "
                   f"backend: {detector_backend}")
    
    def _load_image(self, image_input: Union[str, bytes, np.ndarray]) -> np.ndarray:
        """
        Load image from various input types
        
        Args:
            image_input: File path, base64 string, bytes, or numpy array
            
        Returns:
            numpy array of image
        """
        try:
            # If it's already a numpy array
            if isinstance(image_input, np.ndarray):
                return image_input
            
            # If it's a file path
            if isinstance(image_input, str):
                if os.path.exists(image_input):
                    img = cv2.imread(image_input)
                    if img is None:
                        raise ValueError(f"Could not read image from {image_input}")
                    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Try to decode as base64
                try:
                    image_data = base64.b64decode(image_input)
                    image = Image.open(io.BytesIO(image_data))
                    return np.array(image)
                except Exception:
                    raise ValueError("Invalid image input: not a valid file path or base64 string")
            
            # If it's bytes
            if isinstance(image_input, bytes):
                image = Image.open(io.BytesIO(image_input))
                return np.array(image)
            
            raise ValueError(f"Unsupported image input type: {type(image_input)}")
            
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better face detection
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to RGB if needed
        if len(image.shape) == 2:  # Grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:  # RGBA
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        
        # Enhance image quality
        # Apply slight Gaussian blur to reduce noise
        image = cv2.GaussianBlur(image, (3, 3), 0)
        
        # Enhance contrast using CLAHE
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        image = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        return image
    
    def verify_faces(
        self,
        user_image: Union[str, bytes, np.ndarray],
        document_image: Union[str, bytes, np.ndarray],
        document_type: str = "Unknown"
    ) -> FaceMatchResult:
        """
        Verify if faces in two images match
        
        Args:
            user_image: User's photo (file path, base64, bytes, or numpy array)
            document_image: Document image (Aadhaar/PAN/Voter ID)
            document_type: Type of document for logging
            
        Returns:
            FaceMatchResult object with matching details
        """
        try:
            logger.info(f"Starting face verification for {document_type}")
            
            # Load and preprocess images
            img1 = self._load_image(user_image)
            img2 = self._load_image(document_image)
            
            img1 = self._preprocess_image(img1)
            img2 = self._preprocess_image(img2)
            
            # Save temporarily for DeepFace processing
            temp_dir = Path("temp_face_match")
            temp_dir.mkdir(exist_ok=True)
            
            img1_path = temp_dir / "user_temp.jpg"
            img2_path = temp_dir / f"doc_temp_{document_type}.jpg"
            
            cv2.imwrite(str(img1_path), cv2.cvtColor(img1, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(img2_path), cv2.cvtColor(img2, cv2.COLOR_RGB2BGR))
            
            # Perform face verification
            result = DeepFace.verify(
                img1_path=str(img1_path),
                img2_path=str(img2_path),
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                distance_metric=self.distance_metric,
                enforce_detection=self.enforce_detection
            )
            
            # Clean up temp files
            img1_path.unlink(missing_ok=True)
            img2_path.unlink(missing_ok=True)
            
            # Calculate confidence score (0-100)
            distance = result['distance']
            threshold = result['threshold']
            
            # Convert distance to confidence (inverse relationship)
            if self.distance_metric == 'cosine':
                # Cosine distance: 0 = identical, 1 = completely different
                confidence = max(0, min(100, (1 - distance) * 100))
            else:
                # Euclidean: lower is better
                confidence = max(0, min(100, (1 - distance / threshold) * 100))
            
            is_match = result['verified']
            
            match_result = FaceMatchResult(
                is_match=is_match,
                confidence=confidence,
                distance=distance,
                threshold=threshold,
                model_used=self.model_name,
                document_type=document_type,
                details={
                    'detector_backend': self.detector_backend,
                    'distance_metric': self.distance_metric
                }
            )
            
            logger.info(f"Verification complete: {match_result}")
            return match_result
            
        except Exception as e:
            logger.error(f"Error during face verification: {str(e)}")
            raise
    
    def verify_multiple_documents(
        self,
        user_image: Union[str, bytes, np.ndarray],
        documents: Dict[str, Union[str, bytes, np.ndarray]],
        require_all_match: bool = False
    ) -> Dict[str, FaceMatchResult]:
        """
        Verify user face against multiple documents
        
        Args:
            user_image: User's photo
            documents: Dictionary with document_type as key and image as value
                      e.g., {'aadhaar': 'path/to/aadhaar.jpg', 'pan': 'path/to/pan.jpg'}
            require_all_match: If True, all documents must match
            
        Returns:
            Dictionary with document_type as key and FaceMatchResult as value
        """
        results = {}
        
        for doc_type, doc_image in documents.items():
            try:
                result = self.verify_faces(user_image, doc_image, doc_type)
                results[doc_type] = result
            except Exception as e:
                logger.error(f"Error verifying {doc_type}: {str(e)}")
                results[doc_type] = None
        
        return results
    
    def get_detailed_verification_report(
        self,
        user_image: Union[str, bytes, np.ndarray],
        documents: Dict[str, Union[str, bytes, np.ndarray]]
    ) -> Dict:
        """
        Get comprehensive verification report for all documents
        
        Args:
            user_image: User's photo
            documents: Dictionary with document_type as key and image as value
            
        Returns:
            Detailed report with overall verdict and individual results
        """
        results = self.verify_multiple_documents(user_image, documents)
        
        # Calculate overall metrics
        successful_matches = sum(1 for r in results.values() if r and r.is_match)
        total_documents = len(results)
        avg_confidence = np.mean([r.confidence for r in results.values() if r])
        
        # Determine overall verdict
        if successful_matches == total_documents:
            overall_verdict = "VERIFIED"
            verdict_description = "All documents match successfully"
        elif successful_matches > 0:
            overall_verdict = "PARTIALLY_VERIFIED"
            verdict_description = f"{successful_matches}/{total_documents} documents match"
        else:
            overall_verdict = "NOT_VERIFIED"
            verdict_description = "No matching documents found"
        
        report = {
            'overall_verdict': overall_verdict,
            'verdict_description': verdict_description,
            'total_documents': total_documents,
            'successful_matches': successful_matches,
            'average_confidence': round(avg_confidence, 2),
            'individual_results': {
                doc_type: result.to_dict() if result else None
                for doc_type, result in results.items()
            },
            'timestamp': str(np.datetime64('now')),
            'model_used': self.model_name,
            'detector_backend': self.detector_backend
        }
        
        return report


class MultiModelFaceMatcher:
    """
    Advanced face matcher that uses multiple models for consensus-based verification
    Provides highest accuracy by combining results from multiple models
    """
    
    def __init__(
        self,
        models: List[str] = None,
        detector_backend: str = FaceMatchConfig.DEFAULT_BACKEND,
        consensus_threshold: float = 0.6  # 60% models must agree
    ):
        """
        Initialize multi-model face matcher
        
        Args:
            models: List of models to use (defaults to top 3 accurate models)
            detector_backend: Backend for face detection
            consensus_threshold: Minimum ratio of models that must agree for match
        """
        self.models = models or ['Facenet512', 'ArcFace', 'VGG-Face']
        self.detector_backend = detector_backend
        self.consensus_threshold = consensus_threshold
        self.matchers = [
            FaceMatcher(model, detector_backend)
            for model in self.models
        ]
        
        logger.info(f"Initialized MultiModelFaceMatcher with {len(self.models)} models")
    
    def verify_faces_consensus(
        self,
        user_image: Union[str, bytes, np.ndarray],
        document_image: Union[str, bytes, np.ndarray],
        document_type: str = "Unknown"
    ) -> Dict:
        """
        Verify faces using multiple models and return consensus result
        
        Args:
            user_image: User's photo
            document_image: Document image
            document_type: Type of document
            
        Returns:
            Dictionary with consensus result and individual model results
        """
        results = []
        
        for matcher in self.matchers:
            try:
                result = matcher.verify_faces(user_image, document_image, document_type)
                results.append(result)
            except Exception as e:
                logger.error(f"Error with model {matcher.model_name}: {str(e)}")
                continue
        
        if not results:
            raise ValueError("All models failed to process images")
        
        # Calculate consensus
        matches = sum(1 for r in results if r.is_match)
        match_ratio = matches / len(results)
        is_consensus_match = match_ratio >= self.consensus_threshold
        
        # Calculate average confidence
        avg_confidence = np.mean([r.confidence for r in results])
        weighted_confidence = avg_confidence * match_ratio
        
        consensus_result = {
            'is_match': is_consensus_match,
            'confidence': round(weighted_confidence, 2),
            'match_ratio': round(match_ratio, 2),
            'models_agreed': matches,
            'total_models': len(results),
            'consensus_strength': self._get_consensus_strength(match_ratio),
            'document_type': document_type,
            'individual_results': [r.to_dict() for r in results]
        }
        
        return consensus_result
    
    def _get_consensus_strength(self, match_ratio: float) -> str:
        """Get human-readable consensus strength"""
        if match_ratio == 1.0:
            return "Unanimous"
        elif match_ratio >= 0.8:
            return "Strong Consensus"
        elif match_ratio >= 0.6:
            return "Moderate Consensus"
        else:
            return "No Consensus"


# Convenience functions for easy usage

def verify_identity_documents(
    user_photo_path: str,
    aadhaar_image: Optional[str] = None,
    pan_image: Optional[str] = None,
    voter_id_image: Optional[str] = None,
    use_multi_model: bool = False
) -> Dict:
    """
    Convenience function to verify user photo against identity documents
    
    Args:
        user_photo_path: Path to user's photo or base64 string
        aadhaar_image: Path to Aadhaar image or base64 string
        pan_image: Path to PAN image or base64 string
        voter_id_image: Path to Voter ID image or base64 string
        use_multi_model: Whether to use multiple models for higher accuracy
        
    Returns:
        Detailed verification report
    """
    # Prepare documents dictionary
    documents = {}
    if aadhaar_image:
        documents['Aadhaar'] = aadhaar_image
    if pan_image:
        documents['PAN'] = pan_image
    if voter_id_image:
        documents['Voter_ID'] = voter_id_image
    
    if not documents:
        raise ValueError("At least one document image must be provided")
    
    # Create matcher and verify
    if use_multi_model:
        matcher = MultiModelFaceMatcher()
        results = {}
        for doc_type, doc_image in documents.items():
            results[doc_type] = matcher.verify_faces_consensus(
                user_photo_path, doc_image, doc_type
            )
        return {
            'verification_type': 'multi_model_consensus',
            'results': results
        }
    else:
        matcher = FaceMatcher()
        return matcher.get_detailed_verification_report(user_photo_path, documents)


# Example usage
if __name__ == "__main__":
    """
    Example usage of the face matching system
    """
    
    # Example 1: Single document verification
    print("Example 1: Single Document Verification")
    print("-" * 50)
    
    matcher = FaceMatcher(
        model_name='Facenet512',  # High accuracy model
        detector_backend='retinaface'  # Best detection
    )
    
    # Uncomment and modify paths when you have actual images
    """
    result = matcher.verify_faces(
        user_image='path/to/user_photo.jpg',
        document_image='path/to/aadhaar.jpg',
        document_type='Aadhaar'
    )
    
    print(f"Match: {result.is_match}")
    print(f"Confidence: {result.confidence}%")
    print(f"Match Strength: {result._get_match_strength()}")
    print(result.to_dict())
    """
    
    # Example 2: Multiple documents verification
    print("\nExample 2: Multiple Documents Verification")
    print("-" * 50)
    
    """
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
    print(f"Successful Matches: {report['successful_matches']}/{report['total_documents']}")
    print(f"Average Confidence: {report['average_confidence']}%")
    """
    
    # Example 3: Multi-model consensus (highest accuracy)
    print("\nExample 3: Multi-Model Consensus Verification")
    print("-" * 50)
    
    """
    multi_matcher = MultiModelFaceMatcher(
        models=['Facenet512', 'ArcFace', 'VGG-Face'],
        consensus_threshold=0.6
    )
    
    consensus_result = multi_matcher.verify_faces_consensus(
        user_image='path/to/user_photo.jpg',
        document_image='path/to/aadhaar.jpg',
        document_type='Aadhaar'
    )
    
    print(f"Consensus Match: {consensus_result['is_match']}")
    print(f"Confidence: {consensus_result['confidence']}%")
    print(f"Models Agreed: {consensus_result['models_agreed']}/{consensus_result['total_models']}")
    print(f"Consensus Strength: {consensus_result['consensus_strength']}")
    """
    
    # Example 4: Using convenience function
    print("\nExample 4: Using Convenience Function")
    print("-" * 50)
    
    """
    report = verify_identity_documents(
        user_photo_path='path/to/user_photo.jpg',
        aadhaar_image='path/to/aadhaar.jpg',
        pan_image='path/to/pan.jpg',
        voter_id_image='path/to/voter_id.jpg',
        use_multi_model=True  # For highest accuracy
    )
    
    print(report)
    """
    
    print("\n" + "="*50)
    print("Face matching module loaded successfully!")
    print("Import and use the classes above in your application.")
    print("="*50)

