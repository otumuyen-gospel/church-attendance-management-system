from django.db import models
from capturemethod.models import CaptureMethod
from services.models import Services
from person.models import Person
from auditlog.registry import auditlog
from django.db.models import UniqueConstraint, Q
from django.db.models.functions import TruncDate
from person.models import Person

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
        # Enforce uniqueness for the combination of 'personId' and the date part of 'checkInTimestamp'
        constraints = [
            UniqueConstraint(
                # Use TruncDate to extract only the date part for the constraint
                # Note: TruncDate requires a supported database like PostgreSQL, MySQL, or Oracle.
                # SQLite has limitations with functional indexes/constraints.
                # If using SQLite, see the "Alternative for SQLite" section below.
                TruncDate('checkInTimestamp'),
                fields=['personId'],
                name='unique_person_date_attendance'
            )
        ]

    def __str__(self):
        return f'{self.personId.firstName} {self.personId.lastName}'
    

auditlog.register(Attendance)