from django.db import models
from auditlog.registry import auditlog

# Create your models here.

class Church(models.Model):
    name = models.TextField(blank=False)
    address = models.TextField(blank=False)
    description = models.TextField(blank=False)
    logo = models.CharField(max_length=500, blank=False, default="welcome")
    class Meta:
        ordering = ('name',)
    def __str__(self):
        return f"{self.name}"

auditlog.register(Church)