from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
import pytz
from django.utils import timezone
from django.conf import settings
from .models import User, Semester, Course, Offering, Location, LineItem, Order

# timezone.activate(pytz.timezone(settings.DEFAULT_TIMEZONE))

# Register your models here.
admin.site.register(User)
admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(Offering)
admin.site.register(Location)
admin.site.register(Order)
admin.site.register(LineItem)

