from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Faces
from .cache import FacesCache


@receiver(post_save, sender=Faces)
def invalidate_faces_cache_on_save(sender, instance, **kwargs):
    """Invalidate cache when a face is saved (created or updated)"""
    FacesCache.invalidate_cache()


@receiver(post_delete, sender=Faces)
def invalidate_faces_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when a face is deleted"""
    FacesCache.invalidate_cache()