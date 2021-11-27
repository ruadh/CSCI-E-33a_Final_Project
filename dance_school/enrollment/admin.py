from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import User, Semester, Course, Offering, Location, Enrollment, Order

# Register your models here.
admin.site.register(User)
admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(Offering)
admin.site.register(Location)
admin.site.register(Order)
admin.site.register(Enrollment)