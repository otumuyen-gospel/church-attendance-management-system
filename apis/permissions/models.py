from django.db import models

# Create your models here.
class Permissions(models.Model):
    permission = models.TextField(blank=False)

    class Meta:
        ordering = ('permission',)
    def __str__(self):
        return f'{self.permission}'