import numpy as np
from django.core.cache import cache
from .models import Faces


class FacesCache:
    """
    Efficient cache manager for Faces model to speed up face recognition.
    Uses Django's cache framework with in-memory storage for fast access.
    """

    CACHE_KEY_DATA = 'faces_data'
    CACHE_TIMEOUT = 3600  # 1 hour

    @classmethod
    def get_cache_data(cls):
        """
        Get all faces data from cache, loading from DB if not cached.
        Returns list of dicts with id, encoding, name.
        """
        data = cache.get(cls.CACHE_KEY_DATA)
        if data is None:
            cls._load_cache()
            data = cache.get(cls.CACHE_KEY_DATA)
        return data or []

    @classmethod
    def get_all_encodings(cls):
        """
        Get all face encodings from cache.
        Returns list of numpy arrays.
        """
        data = cls.get_cache_data()
        return [item['encoding'] for item in data]

    @classmethod
    def get_face_names(cls):
        """
        Get all face names from cache.
        Returns list of strings.
        """
        data = cls.get_cache_data()
        return [item['name'] for item in data]

    @classmethod
    def get_face_ids(cls):
        """
        Get all face IDs from cache.
        Returns list of integers.
        """
        data = cls.get_cache_data()
        return [item['id'] for item in data]

    @classmethod
    def _load_cache(cls):
        """
        Load all faces from database into cache.
        """
        faces = Faces.objects.select_related('personId').all()
        data = []

        for face in faces:
            if face.encoding:
                data.append({
                    'id': face.id,
                    'encoding': np.array(face.encoding),
                    'name': f"{face.personId.firstName} {face.personId.lastName}"
                })

        cache.set(cls.CACHE_KEY_DATA, data, cls.CACHE_TIMEOUT)

    @classmethod
    def invalidate_cache(cls):
        """
        Clear the cache, forcing reload on next access.
        """
        cache.delete(cls.CACHE_KEY_DATA)

    @classmethod
    def refresh_cache(cls):
        """
        Force refresh cache from database.
        """
        cls.invalidate_cache()
        cls._load_cache()