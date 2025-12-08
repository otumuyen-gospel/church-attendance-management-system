from django.db import models
from person.models import Person
from  church.models import Church
from role.models import Role
from ministries.models import Ministries
from auditlog.registry import auditlog

# Create your models here.
class Leadership(models.Model):
    personId = models.ForeignKey(Person, on_delete=models.CASCADE)
    churchId = models.ForeignKey(Church, on_delete=models.CASCADE)
    ministryId = models.ForeignKey(Ministries, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    roleId = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True )

    description = models.TextField(blank=False)

    def __str__(self):
        return f'{self.roleId.name}'

auditlog.register(Leadership)