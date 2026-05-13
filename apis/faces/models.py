from django.db import models
from person.models import Person
from encrypted_json_fields.fields import EncryptedJSONField

# Create your models here.
class Faces(models.Model):
    pics = models.CharField(max_length=500, blank=False, default="welcome")
    personId = models.ForeignKey(Person, on_delete=models.CASCADE)
    encoding = EncryptedJSONField(null=False, default=dict) # Stores the 128-d vector

    def __str__(self):
        return f'{self.personId.firstName} {self.personId.lastName}'