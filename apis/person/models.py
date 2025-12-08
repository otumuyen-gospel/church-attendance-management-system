from django.db import models
from church.models import Church
from household.models import HouseHold
from membership.models import Membership
from django.utils import timezone
from auditlog.registry import auditlog

# Create your models here.
class Person(models.Model):
    churchId = models.ForeignKey(Church,on_delete=models.CASCADE)
    householdId = models.ForeignKey(HouseHold, on_delete=models.SET_NULL, null=True, blank=True)
    membershipId = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True)
    firstName = models.TextField(blank=False)
    lastName = models.TextField(blank=False)
    middleName = models.TextField(blank=False)
    dob = models.DateField(blank=False)
    phone = models.CharField(blank=False, max_length=11)
    email = models.EmailField(blank=False)
    entranceDate = models.DateTimeField(blank=False)
    faceEncoding = models.BinaryField(null=True, blank=True)

    class Meta:
        ordering = ('firstName','lastName',)
    def __str__(self):
        return f'{self.lastName} {self.firstName}'
    @property
    def age(self):
        today = timezone.now().date()
        age = today.year - self.dob.year
        if (today.month, today.day) < (self.dob.month, self.dob.day):
            age -= 1 #is not yet birthday so subtract 1 from age
        return age
    

auditlog.register(Person)