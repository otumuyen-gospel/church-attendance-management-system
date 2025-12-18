
# Create your models here.
import uuid
from django.contrib.auth.models import (AbstractBaseUser, 
BaseUserManager, PermissionsMixin)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404
import random 
from datetime import timedelta
from django.utils import timezone
from role.models import Role
from person.models import Person
from .usermanager import AccountManager
from auditlog.registry import auditlog


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True)
    username = models.CharField(max_length=11, unique=True)
    is_active = models.BooleanField(default=True)
    '''for administrators only'''
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    '''this fields must be entered or unique'''
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','roleId','is_staff','is_active',
                       'is_superuser', 'personId']
    roleId = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    personId = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    

    otp = models.CharField(max_length=6, blank=True, null=True, default=None)
    otp_exp = models.DateTimeField(blank=True, null=True, default=None) 
    otp_verified = models.BooleanField(default=False)

    objects = AccountManager()
    class Meta:
        ordering = ('username',)
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP
        self.otp_exp = timezone.now() + timedelta(minutes=10)
        self.otp_verified = False
        self.save()
    def __str__(self):
        return f"{self.username}"
    @property
    def name(self):
        return f"{self.username}"
    

auditlog.register(User)