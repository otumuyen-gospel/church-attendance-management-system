from django.db import models

# Create your models here.
class Membership(models.Model):
    status = models.TextField(blank=False)
    description = models.TextField(blank=False)

    class Meta:
        ordering = ("status",)
    def __str__(self):
        return f'{self.status}'