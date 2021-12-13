'''Admin area customizations for the Enrollment app in Django project Dance School'''

# CITATION:     Import sorting by iSort, as recommended by the Django contributors documentation:
#               https://github.com/PyCQA/isort#readme

# from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Course,
    GiftCard,
    LineItem,
    Location,
    Offering,
    Order,
    Semester,
    User,
    Vacation,
)

# Inlines - For adding related table data to a model's detail views


class LineItemStackedInline(admin.StackedInline):
    '''Adds an inline for managing related line items'''
    model = LineItem
    extra = 0


class OfferingTabularInline(admin.TabularInline):
    '''Adds an inline for managing related offerings'''
    model = Offering
    extra = 0


class VacationTabularInline(admin.TabularInline):
    '''Adds an inline for managing related vacation date spans'''
    model = Vacation
    extra = 0


# List views - Customize the list/summary views for a model


class LineItemAdmin(admin.ModelAdmin):
    '''Primary admin area for line items'''
    list_display = ('order', 'offering', 'price')
    ordering = ('-id',)


class OrderAdmin(admin.ModelAdmin):
    '''Primary admin area for orders'''
    readonly_fields = ('subtotal', 'total')
    inlines = [LineItemStackedInline]
    list_display = ('student', 'completed', 'subtotal', 'discount', 'total')
    ordering = ('-id',)


class OfferingAdmin(admin.ModelAdmin):
    '''Primary admin area for offerings'''
    list_display = ('semester', 'course', 'weekday', 'start_time',
                    'location', 'spots_left', 'contact_sheet')
    readonly_fields = ('price', 'offering_dates',
                       'no_class_dates', 'num_weeks')

    # CITATION:  https://stackoverflow.com/a/32220985
    def contact_sheet(self, obj):
        '''Provides a link to the contact sheet URL for the current offering'''
        return mark_safe('<a href="{}">Contact Sheet</a>'.format(
            reverse('contact_sheet', args=[obj.pk])
        ))


class SemesterAdmin(admin.ModelAdmin):
    '''Primary admin area for semesters'''
    inlines = [VacationTabularInline, OfferingTabularInline]
    ordering = ('-start_date',)


class UserAdmin(admin.ModelAdmin):
    '''Primary admin area for users/students'''
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('last_name', 'first_name')


class GiftCardAdmin(admin.ModelAdmin):
    '''Primary admin area for gift cards'''
    list_display = ('__str__', 'amount')


class CourseAdmin(admin.ModelAdmin):
    '''Primary admin area for courses'''
    ordering = ('title',)


class LocationAdmin(admin.ModelAdmin):
    '''Primary admin area for locations'''
    ordering = ('name',)

class VacationAdmin(admin.ModelAdmin):
    '''Primary admin area for vacations'''
    list_display = ('start_date', 'end_date')
    ordering = ('start_date',)


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Offering, OfferingAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(LineItem, LineItemAdmin)
admin.site.register(GiftCard, GiftCardAdmin)
admin.site.register(Vacation, VacationAdmin)
