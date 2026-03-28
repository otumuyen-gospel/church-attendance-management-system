from django.apps import AppConfig


class FacesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faces'

    def ready(self):
        import faces.signals  # noqa
