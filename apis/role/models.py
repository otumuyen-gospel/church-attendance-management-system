from django.db import models
from auditlog.registry import auditlog
# Create your models here.
class Role(models.Model):
    name = models.TextField(blank=False, unique=True)
    description = models.TextField(blank=False)
    permissions = models.TextField(blank=False)

    class Meta:
        ordering= ('name',)
    def __str__(self):
        return f"{self.name}"

auditlog.register(Role)