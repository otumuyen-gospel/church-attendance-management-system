# Create your models here.
from django.db import models

# Create your models here.
class Myapp(models.Model):
    remark = models.TextField(blank=True)
    class Meta:
        ordering = ('remark',)
    def __str__(self):
        return f"{self.remark}"