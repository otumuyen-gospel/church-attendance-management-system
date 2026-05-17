from django.db import models
from user.models import User
from person.models import Person
from auditlog.registry import auditlog

# Create your models here.
class Followup(models.Model):
    type = models.CharField(max_length=255, blank=False, default="visitor followup")
    followeeId = models.ForeignKey(Person, on_delete=models.CASCADE)
    followerId = models.ForeignKey(User, on_delete=models.CASCADE)
    creatorId = models.ForeignKey(User, on_delete=models.SET_NULL, 
        null=True, 
        blank=True, default=None,  related_name='creator')
    dueDate = models.DateField()

    STATUS_PENDING = 'PENDING'
    STATUS_DONE = 'COMPLETED'
    STATUSES = [
        (STATUS_PENDING,'PENDING'),
        (STATUS_DONE, 'COMPLETED'),
    ]
    status = models.CharField(choices=STATUSES,
                               default=STATUS_PENDING)

    comment = models.CharField(max_length=500)

    class Meta:
        ordering = ('status','dueDate')
    def __str__(self):
        return f'{self.followeeId.firstName} {self.followeeId.lastName}'


auditlog.register(Followup)