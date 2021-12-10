from django.db.models.deletion import PROTECT
import pytz
# from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum, Count
from django.core.exceptions import ValidationError
from markdown2 import Markdown


# Timezones list approach from:  https://stackoverflow.com/a/45867250
TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

# Create your models here.


class User(AbstractUser):
    # Required info
    timezone = models.CharField(max_length=32, choices=TIMEZONES,
                                default=settings.DEFAULT_TIMEZONE)
    first_name = models.CharField(max_length=128, null=False, blank=False)
    last_name = models.CharField(max_length=128, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    # Non-required info
    phone = models.CharField(max_length=32, null=True, blank=True)
    emergency_first = models.CharField(max_length=128, null=True, blank=True)
    emergency_last = models.CharField(max_length=128, null=True, blank=True)
    emergency_email = models.EmailField(max_length=254, null=True, blank=True)
    emergency_phone = models.CharField(max_length=32, null=True, blank=True)
    accept_terms = models.DateTimeField(null=True, blank=True)
    contact_sheet_notes = models.CharField(max_length=2048, null=True, blank=True)

    # TEMP FOR TESTING
    @property
    def current_time(self):
        return timezone.now()

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.username})'

    # CITATION:     Adapted from provided models.py in Project 3
    def serialize_editable(self):
        """Returns a JSON object containing the user's editable profile fields with dashes instead of underscores in names"""
        profile = {}
        for field in settings.EDITABLE_USER_FIELDS:
            profile[field.replace('_', '-')] = getattr(self, field)
        return profile



class Location(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)
    address_1 = models.CharField(max_length=1024, null=False, blank=False)
    address_2 = models.CharField(max_length=1024, null=True, blank=True)
    city = models.CharField(max_length=256, null=False, blank=False)
    state = models.CharField(max_length=2, null=False, blank=False)
    zip = models.CharField(max_length=10, null=True, blank=True)
    parking = models.CharField(max_length=2048, null=True, blank=True)
    web_site = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class Semester(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    registration_open = models.DateTimeField(null=False, blank=False)
    registration_close = models.DateTimeField(null=False, blank=False)
    recital_date = models.DateTimeField(null=True, blank=True)
    hide = models.BooleanField(default=True, null=True, blank=True)

    # CITATION:  https://stackoverflow.com/a/54011108
    def clean(self):
        # Clean is applied before required fields are checked, so we have to double-check here
        if self.start_date != None and self.end_date != None and self.registration_open != None and self.registration_close != None:
            if self.start_date >= self.end_date:
                raise ValidationError(
                    'Start date must be earlier than end date')
            if self.registration_open >= self.registration_close:
                raise ValidationError(
                    'Registration open must be earlier than registration close')

    @property
    def registration_status(self):
        now = timezone.now()
        if self.registration_close < now:
            return 'closed'
        elif self.registration_open > now:
            return 'future'
        else:
            return 'open'

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=64, null=False, blank=False)
    subtitle = models.CharField(max_length=256, null=False, blank=False)
    description = models.TextField(max_length=4096, null=False, blank=False, help_text=settings.MARKDOWN_HELP_TEXT)
    requirements = models.CharField(max_length=256, null=False, blank=False)
    qualifications = models.CharField(max_length=1024, null=False, blank=False)

    @property
    def description_html(self):
        return Markdown().convert(self.description)

    def __str__(self):
        return self.title


class Offering(models.Model):
    course = models.ForeignKey(
        Course, on_delete=PROTECT, null=False, blank=False, related_name='offerings')
    semester = models.ForeignKey(
        Semester, on_delete=PROTECT, null=False, blank=False, related_name='offerings')
    location = models.ForeignKey(
        Location, on_delete=PROTECT, null=False, blank=False, related_name='offerings')
    price = models.DecimalField(
        max_digits=7, decimal_places=2, null=False, blank=False)
    weekday = models.IntegerField(
        choices=settings.WEEKDAYS, null=False, blank=False)
    start_time = models.TimeField(null=False, blank=False)
    end_time = models.TimeField(null=False, blank=False)
    timezone = models.CharField(max_length=32, choices=TIMEZONES,
                                default=settings.DEFAULT_TIMEZONE)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    backup_date = models.DateField(null=False, blank=False)
    capacity = models.IntegerField(null=False, blank=False)
    schedule_notes = models.CharField(max_length=2048, null=True, blank=True)
    notes = models.CharField(max_length=2048, null=True, blank=True)

    @property
    def weekday_name(self):
        return settings.WEEKDAYS[self.weekday][1]

    @property
    def spots_left(self):
        try:
            sold = self.line_items.exclude(order__completed=None).aggregate(Count('id'))['id__count']
        except Exception:
            sold = 0
        return self.capacity - sold

    # CITATION:  https://stackoverflow.com/a/54011108
    def clean(self):
        # Clean is applied before required fields are checked, so we have to double-check here
        if self.start_date != None and self.end_date != None and self.start_time != None and self.end_time != None and self.backup_date != None:
            if self.start_date >= self.end_date:
                raise ValidationError(
                    'Start date must be earlier than end date')
            if self.start_time >= self.end_time:
                raise ValidationError(
                    'Start time must be earlier than end time')
            if self.start_date >= self.backup_date:
                raise ValidationError(
                    'Backup date must be later than start date')

    def __str__(self):
        return f'{self.course.title} - {self.weekday_name}s - {self.semester.name}'


class Order(models.Model):
    student = models.ForeignKey(
        User, on_delete=PROTECT, null=False, blank=False, related_name='orders')
    discount = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)

    @property
    def subtotal(self):
        try:
            amount = self.line_items.aggregate(Sum('price'))['price__sum']
        except Exception:
            return 0
        return 0 if amount == None else amount

    @property
    def total(self):
        return self.subtotal - self.discount if self.discount != None else self.subtotal

    @property
    def semester(self):
        return self.line_items.first().offering.semester.name

    def __str__(self):
        if self.completed == None:
            date_string = 'incomplete'
        else:
            date_string = self.completed.strftime("%x %X")
        return f'{self.student} - {date_string}'


class LineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=PROTECT,
                              null=False, blank=False, related_name='line_items')
    offering = models.ForeignKey(
        Offering, on_delete=PROTECT, null=False, blank=False, related_name='line_items')
    planned_absences = models.CharField(max_length=1024, null=True, blank=True)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, blank=False)

    def __str__(self):
        return f'{self.offering.course.title} {self.offering.weekday_name} {self.offering.semester.name}'

    # CITATION:     Adapted from provided models.py in Project 3
    def serialize(self):
        return {
            'id': self.id,
            'offering_display': f'{self.offering.course.title} {self.offering.weekday_name}',
            'price': self.offering.price
        }

class GiftCard(models.Model):
    card_number = models.CharField(max_length=16, null=False, blank=False)
    month = models.CharField(max_length=2, null=False, blank=False)
    year = models.CharField(max_length=4, null=False, blank=False)
    pin = models.CharField(max_length=4, null=False, blank=False)
    amount = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False)

    # Display the last 4 digits
    def __str__(self):
        return f'x{self.card_number[-4:]}'
