from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    phone = models.CharField(max_length=32, null=True, blank=True)
    emergency_first = models.CharField(max_length=128, null=True, blank=True)
    emergency_last = models.CharField(max_length=128, null=True, blank=True)
    emergency_email = models.EmailField(max_length=254, null=True, blank=True)
    emergency_phone = models.CharField(max_length=32, null=True, blank=True)
    accept_terms = models.BooleanField(null=True, blank=True)
    