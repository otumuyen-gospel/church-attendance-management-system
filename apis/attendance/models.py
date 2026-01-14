from django.db import models
from django.utils import timezone
from capturemethod.models import CaptureMethod
from services.models import Services
from person.models import Person
from auditlog.registry import auditlog
from django.db.models import UniqueConstraint, Q

# Create your models here.
class Attendance(models.Model):
    personId = models.ForeignKey(Person, on_delete=models.CASCADE)
    servicesId = models.ForeignKey(Services, on_delete=models.CASCADE)
    captureMethodId = models.ForeignKey(CaptureMethod,  on_delete=models.SET_NULL,
                                   null=True, blank=True)
    
    checkInTimestamp = models.DateTimeField(blank=False, auto_now_add=True)
    attendanceDate = models.DateField(blank=False, auto_now_add=True)
    checkOutTimestamp = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('comment','attendanceDate',)
        # Enforce uniqueness for the combination of 'personId' and attendance date
        constraints = [
            UniqueConstraint(
                fields=['personId', 'attendanceDate'],
                name='unique_person_date_attendance'
            )
        ]

    def __str__(self):
        return f'{self.personId.firstName} {self.personId.lastName}'
    

auditlog.register(Attendance)