from celery import shared_task
import face_recognition
import numpy as np
from django.core.files.base import ContentFile
from .models import Faces
from .cache import FacesCache
from person.models import Person


@shared_task
def process_face_creation(person_id, image_files_data):
    """
    Background task to process face creation.
    image_files_data: list of dicts with 'name' and 'content' (bytes)
    """
    try:
        person = Person.objects.get(id=person_id)

        all_encodings = []
        saved_files = []

        for img_data in image_files_data:
            # Create ContentFile from bytes
            content_file = ContentFile(img_data['content'], name=img_data['name'])

            # Load and encode
            img = face_recognition.load_image_file(content_file)
            encodings = face_recognition.face_encodings(img, num_jitters=10)
            if encodings:
                all_encodings.append(encodings[0])
                saved_files.append(content_file)

        if not all_encodings:
            return {'success': False, 'error': 'No faces detected'}

        # Average the encodings
        avg_encoding = np.mean(all_encodings, axis=0).tolist()

        # Create face record
        face = Faces.objects.create(
            personId=person,
            encoding=avg_encoding,
            pics=saved_files[0] if saved_files else None
        )

        # Invalidate cache
        FacesCache.invalidate_cache()

        return {
            'success': True,
            'message': f'Face registered for {person.firstName} {person.lastName}',
            'face_id': face.id
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


@shared_task
def process_face_update(face_id, image_files_data):
    """
    Background task to process face update.
    """
    try:
        face = Faces.objects.get(id=face_id)

        all_encodings = []
        saved_files = []

        for img_data in image_files_data:
            content_file = ContentFile(img_data['content'], name=img_data['name'])

            img = face_recognition.load_image_file(content_file)
            encodings = face_recognition.face_encodings(img, num_jitters=10)
            if encodings:
                all_encodings.append(encodings[0])
                saved_files.append(content_file)

        if not all_encodings:
            return {'success': False, 'error': 'No faces detected'}

        # Average the encodings
        avg_encoding = np.mean(all_encodings, axis=0).tolist()

        # Update face record
        face.encoding = avg_encoding
        face.pics = saved_files[0] if saved_files else face.pics
        face.save()

        # Invalidate cache
        FacesCache.invalidate_cache()

        return {
            'success': True,
            'message': f'Face updated for {face.personId.firstName} {face.personId.lastName}',
            'face_id': face.id
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}