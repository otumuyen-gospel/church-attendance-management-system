from django.db import models
from auditlog.registry import auditlog
from person.models import Person
# Model for church departments and ministries
class Message(models.Model):
    title = models.TextField(blank=False)
    detail = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True, blank=False)
    recipients = models.EmailField(blank=False)
    senderId = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ('date',)
    def __str__(self):
        return f'{self.title}'
    
auditlog.register(Message)
