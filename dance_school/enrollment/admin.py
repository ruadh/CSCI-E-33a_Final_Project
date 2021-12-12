from django.contrib import admin
from django.db.models import fields
# from django.contrib.auth.admin import UserAdmin
import pytz
from django.utils import timezone
# from django.utils.html import format_html
from django.utils.safestring import mark_safe  
from django.urls import reverse
from django.conf import settings
from .models import User, Semester, Course, Offering, Location, LineItem, Order, GiftCard, Vacation

# TO DO:  Figure out local time zones...
# timezone.activate(pytz.timezone(settings.DEFAULT_TIMEZONE))
# timezone.activate('America/New_York')

# Inlines - For adding related table data to a model's detail views
class LineItemStackedInline(admin.StackedInline):
    model = LineItem
    # TO DO:  Decide how many slots should be addable at a time
    # extra = 1

class OfferingTabularInline(admin.TabularInline):
    model = Offering
    extra = 0

class VacationTabularInline(admin.TabularInline):
    model = Vacation
    extra = 0

# List views - Customize the list/summary views for a model
class LineItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'offering', 'price')
    ordering = ('-id',)

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('subtotal', 'total')
    inlines = [LineItemStackedInline]
    list_display = ('student', 'completed', 'subtotal', 'discount', 'total')
    ordering = ('-id',)

class OfferingAdmin(admin.ModelAdmin):
    list_display = ('semester', 'course', 'weekday', 'start_time', 'location', 'spots_left', 'contact_sheet')
    readonly_fields = ('price', 'offering_dates', 'no_class_dates', 'num_weeks')

    # CITATION:  https://stackoverflow.com/a/32220985
    def contact_sheet(self, obj):
        return mark_safe('<a href="{}">Contact Sheet</a>'.format(
            reverse("contact_sheet", args=[obj.pk])
        ))

class SemesterAdmin(admin.ModelAdmin):
    inlines = [VacationTabularInline, OfferingTabularInline]
    ordering = ('-start_date',)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name','email', 'phone')
    ordering = ('last_name','first_name')

class GiftCardAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'amount')

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Course)
admin.site.register(Offering, OfferingAdmin)
admin.site.register(Location)
admin.site.register(Order, OrderAdmin)
admin.site.register(LineItem, LineItemAdmin)
admin.site.register(GiftCard, GiftCardAdmin)
admin.site.register(Vacation)
