"""
Celery configuration and tasks (OPTIONAL - for production async processing)

To use Celery:
1. Install: pip install celery[redis]
2. Add 'celery' to INSTALLED_APPS in settings.py
3. Configure in settings.py:
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
4. Run worker: celery -A apis worker -l info
"""

try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Mock decorator for when celery is not installed
    def shared_task(bind=False, **kwargs):
        def decorator(func):
            return func
        return decorator

from django.core.cache import cache
from .tasks import (
    generate_face_encoding_async,
    batch_generate_encodings_async,
    regenerate_all_encodings_async
)
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def celery_generate_face_encoding(self, face_id):
    """
    Celery task for async face encoding generation
    
    Args:
        face_id: ID of the Faces model instance
    """
    try:
        return generate_face_encoding_async(face_id)
    except Exception as exc:
        logger.error(f"Celery task failed for face {face_id}: {str(exc)}")
        # Retry after 60 seconds
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def celery_batch_generate_encodings(self, face_ids=None):
    """
    Celery task for batch encoding generation
    
    Args:
        face_ids: List of face IDs
    """
    try:
        return batch_generate_encodings_async(face_ids)
    except Exception as exc:
        logger.error(f"Celery batch task failed: {str(exc)}")
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def celery_regenerate_all_encodings(self):
    """
    Celery task for regenerating all encodings
    """
    try:
        return regenerate_all_encodings_async()
    except Exception as exc:
        logger.error(f"Celery regeneration task failed: {str(exc)}")
        self.retry(exc=exc, countdown=60)


# Example task integration with face recognition
@shared_task(bind=True)
def celery_batch_face_recognition(self, encoded_face_data, known_encodings_dict):
    """
    Celery task for batch face recognition
    
    Args:
        encoded_face_data: Serialized face encoding
        known_encodings_dict: Dictionary of known encodings
    """
    try:
        import pickle
        import numpy as np
        from .views import FaceRecognitionEngine
        
        # Deserialize
        test_encoding = pickle.loads(encoded_face_data)
        
        # Compare
        matches = FaceRecognitionEngine.compare_faces_efficient(
            test_encoding,
            known_encodings_dict
        )
        
        return {
            'success': True,
            'matches': matches[:5]  # Return top 5
        }
    except Exception as exc:
        logger.error(f"Celery recognition task failed: {str(exc)}")
        return {
            'success': False,
            'error': str(exc)
        }
