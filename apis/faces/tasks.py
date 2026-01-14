"""
Background tasks for face processing
Can be used with Celery or APScheduler for async processing
"""

import pickle
import numpy as np
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
from PIL import Image
import logging
from django.core.cache import cache
from .models import Faces

logger = logging.getLogger(__name__)

def generate_face_encoding_async(face_id):
    """
    Generate face encoding for a given face in background
    
    Args:
        face_id: ID of the Faces model instance
        
    Returns:
        bool: Success status
    """
    try:
        face = Faces.objects.get(id=face_id)
        
        # Process available images
        image_fields = [face.pics, face.pics2, face.pics3]
        encodings_list = []
        
        for image_field in image_fields:
            if image_field:
                try:
                    # Open image
                    image_path = image_field.path
                    image = Image.open(image_path).convert('RGB')
                    image_array = np.array(image)
                    
                    # Detect and encode faces
                    if FACE_RECOGNITION_AVAILABLE:
                        face_locations = face_recognition.face_locations(image_array, model='hog')
                        if face_locations:
                            face_encodings = face_recognition.face_encodings(
                                image_array, 
                                face_locations
                            )
                            if face_encodings:
                                encodings_list.append(face_encodings[0])
                    else:
                        # Fallback: Generate simple encoding from image features
                        from .views import FaceRecognitionEngine
                        encoding, success = FaceRecognitionEngine._generate_simple_encoding(image_array), True
                        if encoding is not None:
                            encodings_list.append(encoding)
                            
                except Exception as e:
                    logger.warning(f"Error encoding image for face {face_id}: {str(e)}")
                    continue
        
        # Combine encodings if multiple found
        if encodings_list:
            if len(encodings_list) > 1:
                combined_encoding = np.mean(encodings_list, axis=0)
            else:
                combined_encoding = encodings_list[0]
            
            # Serialize and save
            face_encoding_bytes = pickle.dumps(combined_encoding)
            face.faceEncoding = face_encoding_bytes
            face.save()
            
            # Clear cache to refresh encodings
            cache.delete("face_encodings_cache")
            
            logger.info(f"Successfully generated encoding for face {face_id}")
            return True
        
        else:
            logger.warning(f"No faces detected in images for face {face_id}")
            return False
            
    except Faces.DoesNotExist:
        logger.error(f"Face {face_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Error generating face encoding for {face_id}: {str(e)}")
        return False


def batch_generate_encodings_async(face_ids=None):
    """
    Batch generate face encodings for multiple faces
    
    Args:
        face_ids: List of face IDs (if None, generates for all without encoding)
        
    Returns:
        dict: Processing results
    """
    try:
        if face_ids:
            faces = Faces.objects.filter(id__in=face_ids)
        else:
            # Generate encodings for faces that don't have one
            faces = Faces.objects.filter(faceEncoding__isnull=True)
        
        total = faces.count()
        success_count = 0
        failed_count = 0
        
        for face in faces:
            if generate_face_encoding_async(face.id):
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(
            f"Batch encoding complete: {success_count}/{total} successful, "
            f"{failed_count} failed"
        )
        
        return {
            'total': total,
            'success': success_count,
            'failed': failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in batch encoding: {str(e)}")
        return {
            'total': 0,
            'success': 0,
            'failed': 0,
            'error': str(e)
        }


def regenerate_all_encodings_async():
    """
    Regenerate all face encodings (useful for updates/fixes)
    
    Returns:
        dict: Processing results
    """
    try:
        faces = Faces.objects.filter(pics__isnull=False)
        total = faces.count()
        success_count = 0
        failed_count = 0
        
        for face in faces:
            if generate_face_encoding_async(face.id):
                success_count += 1
            else:
                failed_count += 1
        
        # Clear cache after all done
        cache.delete("face_encodings_cache")
        
        logger.info(
            f"Regeneration complete: {success_count}/{total} successful, "
            f"{failed_count} failed"
        )
        
        return {
            'total': total,
            'success': success_count,
            'failed': failed_count
        }
        
    except Exception as e:
        logger.error(f"Error regenerating encodings: {str(e)}")
        return {
            'error': str(e)
        }
