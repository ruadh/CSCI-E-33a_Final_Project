import pytz
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    # Timezones list approach from:  https://stackoverflow.com/a/45867250
    timezones = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    timezone = models.CharField(max_length=32, choices=timezones,
                                default=settings.DEFAULT_TIMEZONE)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone = models.CharField(max_length=32, null=True, blank=True)
    emergency_first = models.CharField(max_length=128, null=True, blank=True)
    emergency_last = models.CharField(max_length=128, null=True, blank=True)
    emergency_email = models.EmailField(max_length=254, null=True, blank=True)
    emergency_phone = models.CharField(max_length=32, null=True, blank=True)
    accept_terms = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.username})'