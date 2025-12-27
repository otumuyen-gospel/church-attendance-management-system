from django.db import models
from capturemethod.models import CaptureMethod
from services.models import Services
from person.models import Person
from auditlog.registry import auditlog

# Create your models here.
class Attendance(models.Model):
    personId = models.ForeignKey(Person, on_delete=models.CASCADE)
    servicesId = models.ForeignKey(Services, on_delete=models.CASCADE)
    captureMethodId = models.ForeignKey(CaptureMethod,  on_delete=models.SET_NULL,
                                   null=True, blank=True)
    
    checkInTimestamp = models.DateTimeField(blank=False, auto_now_add=True)
    checkOutTimestamp = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('comment',)
    def __str__(self):
        return f'{self.personId.firstName} {self.personId.lastName}'
    

auditlog.register(Attendance)