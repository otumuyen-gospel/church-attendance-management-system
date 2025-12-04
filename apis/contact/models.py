from django.db import models
from household.models import HouseHold
from person.models import Person

# Create your models here.
class Contact(models.Model):
    personId = models.ForeignKey(Person,on_delete=models.CASCADE)
    householdId = models.ForeignKey(HouseHold, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(blank=False, max_length=11)
    email = models.EmailField(blank=False)
    address = models.TextField(blank=False)
    socialMedia = models.URLField(null=True, blank=True)
    state = models.TextField(blank=False)
    country = models.TextField(blank=False)
    occupation = models.TextField(null=True, blank=True)
    ethnicity = models.TextField(blank=False)
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_OTHERS = 'O'
    USERS_GENDER = [
        (GENDER_MALE,'male'),
        (GENDER_FEMALE, 'female'),
        (GENDER_OTHERS, 'others'),
    ]
    gender = models.CharField(choices=USERS_GENDER,
                               default=GENDER_MALE)
    MARRIED = 'MARRIED'
    SINGLE = 'SINGLE'
    SEPARATED = 'SEPARATED'
    MARITAL_STATUS = [
        (MARRIED, 'MARRIED'),
        (SINGLE,'SINGLE'),
        (SEPARATED,'SEPARATED'),
    ]
    marital_status = models.CharField(choices=MARITAL_STATUS,
                               default=MARRIED)
    
    class Meta:
        ordering = ('marital_status','gender',)
    def __str__(self):
        return f'{self.personId.firstName} {self.personId.lastName}'