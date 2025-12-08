from django.db import models
from church.models import Church
from ministries.models import Ministries
from auditlog.registry import auditlog

# Create your models here.
class Services(models.Model):
    churchId = models.ForeignKey(Church, on_delete=models.CASCADE)
    ministryId = models.ForeignKey(Ministries, on_delete=models.SET_NULL, null=True, blank=True)
    eventName = models.TextField(blank=False)
    eventDate = models.DateField(blank=True, null=True)
    eventTime = models.TimeField(blank=False)
    MONDAY = 'MON'
    TUESDAY = 'TUE'
    WEDNESDAY = 'WED'
    THURSDAY = 'THU'
    FRIDAY = 'FRI'
    SATURDAY = 'SAT'
    SUNDAY = 'SUN'
    EVENT_DAY = [
       (MONDAY, 'MON'),
       (TUESDAY,'TUE'),
       (WEDNESDAY, 'WED'),
       (THURSDAY, 'THU'),
       (FRIDAY, 'FRI'),
       (SATURDAY, 'SAT'),
       (SUNDAY,'SUN'),
    ]
    eventDay = models.CharField(choices=EVENT_DAY,
                               default=SUNDAY,)
    
    location = models.TextField(blank=False)
    isReoccuring = models.BooleanField(default=False)

    class Meta:
        ordering = ("eventName",)
    def __str__(self):
        return f'{self.eventName}'
    
auditlog.register(Services)