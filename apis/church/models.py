from django.db import models
from auditlog.registry import auditlog

# Create your models here.
# Create your models here.
def upload_to(instance, filename):
    return 'church_images_logo_{0}_{1}'.format(instance.id, filename)

class Church(models.Model):
    name = models.TextField(blank=False)
    address = models.TextField(blank=False)
    description = models.TextField(blank=False)
    logo = models.FileField(blank=True, null=True, upload_to=upload_to)
    class Meta:
        ordering = ('name',)
    def __str__(self):
        return f"{self.name}"

auditlog.register(Church)