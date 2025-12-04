from django.db import models
from person.models import Person

# Create your models here.
class FollowUp(models.Model):
    followeeId = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='followee_set')
    followerId = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='follower_set')
    assignment = models.TextField(blank=False)
    dueDate = models.DateField(blank=False)
    isCompleted = models.BooleanField(blank=False, default=False)

    class Meta:
        ordering = ('isCompleted','dueDate',)
    def __str__(self):
        return f'{self.followeeId.lastName} {self.followeeId.firstName}'