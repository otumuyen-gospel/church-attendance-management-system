from django.db import models
from person.models import Person

# Create your models here.
def upload_to(instance, filename):
    return 'user_faces_pics_{0}_{1}'.format(instance.id, filename)

class Faces(models.Model):
    pics = models.FileField(blank=False, upload_to=upload_to)
    personId = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.personId.firstName} {self.personId.lastName}'