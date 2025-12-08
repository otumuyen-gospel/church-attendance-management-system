from django.db import models
from auditlog.registry import auditlog
# Create your models here.
class CaptureMethod(models.Model):
    METHOD_FACE = 'FACE'
    METHOD_FORM = 'FORM'
    CAPTURE_METHODS = [
        (METHOD_FACE,'FACE'),
        (METHOD_FORM,'FORM'),
    ]
    method = models.CharField(choices=CAPTURE_METHODS,
                               default=METHOD_FORM, unique=True)
    
    METHOD_DESCRIPTION_FACE = 'Face Recognition'
    METHOD_DESCRIPTION_FORM = 'Manual Form Entry'
    METHODS_DESCRIPTION = [
        (METHOD_DESCRIPTION_FACE,'Face Recognition'),
        (METHOD_DESCRIPTION_FORM,'Manual Form Entry'),
    ]
    description = models.CharField(choices=METHODS_DESCRIPTION,
                               default=METHOD_DESCRIPTION_FORM, unique=True)
    
    class Meta:
        ordering = ('method',)
    def __str__(self):
        return f"{self.description}"
    
    
auditlog.register(CaptureMethod)