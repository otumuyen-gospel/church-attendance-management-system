from django.apps import AppConfig
from .util import FaceRecognitionHandler

class FacesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faces'
    face_handler = FaceRecognitionHandler()

    def ready(self):
        import faces.signals  # noqa