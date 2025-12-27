from django.db import models
from auditlog.registry import auditlog

# Create your models here.
class HouseHold(models.Model):
    name = models.TextField(blank=False, unique=True)
    address = models.TextField(blank=False)
    count = models.IntegerField(blank=True,null=True)
    head = models.TextField(blank=True,null=True)
    spouse = models.TextField(blank=True,null=True)
    children = models.TextField(blank=True,null=True)

    class Meta:
        ordering = ('name',)
    def __str__(self):
        return f"{self.name}"


auditlog.register(HouseHold)