from django.db import models
from auditlog.registry import auditlog

# Create your models here.
class HouseHold(models.Model):
    name = models.TextField(blank=False)
    address = models.TextField(blank=False)
    count = models.IntegerField(blank=False)
    head = models.TextField(blank=False)
    spouse = models.TextField(blank=False)
    children = models.TextField(blank=False)

    class Meta:
        ordering = ('name',)
    def __str__(self):
        return f"{self.name}"


auditlog.register(HouseHold)