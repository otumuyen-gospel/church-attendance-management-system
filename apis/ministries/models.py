from django.db import models
from church.models import Church

# Model for church departments and ministries
class Ministries(models.Model):
    name = models.TextField(unique=True, blank=False)
    description = models.TextField(blank=False)
    churchId = models.ForeignKey(Church, on_delete=models.CASCADE)

    class Meta:
        ordering = ('name',)
    def __str__(self):
        return f'{self.name}'
