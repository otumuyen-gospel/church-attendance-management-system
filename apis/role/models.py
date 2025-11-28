from django.db import models

# Create your models here.
class Role(models.Model):
    name = models.TextField(blank=False, unique=True)
    description = models.TextField(blank=False)
    permissions = models.JSONField(default=list)

    class Meta:
        ordering= ('name',)
    def __str__(self):
        return f"{self.name}"