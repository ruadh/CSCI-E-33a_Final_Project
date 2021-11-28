from django.contrib.auth.decorators import login_required
# from django.http.request import HttpRequest
# from django.http.response import HttpResponse
import datetime
from django.http.response import HttpResponse
import pytz
# from django.db import models
from django.conf import settings
# from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
# from django import forms

from .models import Offering, Order, User, Semester, Location, Course, LineItem

# AUTHENTICATION
# CITATION:  Adapted from provided starter files in earlier projects


def login_view(request):

    if request.method == 'POST':

        # Attempt to sign user in
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            # Set the display timezone to the user's chosen time
            timezone.activate(user.timezone)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'enrollment/login.html', {
                'message': 'Invalid username and/or password.'
            })
    else:
        return render(request, 'enrollment/login.html')


def logout_view(request):

    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):

    # Gather a list of timezones to populate the timezone choice field in the form
    timezones = pytz.common_timezones

    if request.method == 'POST':

        # Ensure password matches confirmation
        username = request.POST['username']
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            return render(request, 'enrollment/register.html', {
                'message': 'Passwords must match.',
            })
        if password == '':
            return render(request, 'enrollment/register.html', {
                'message': 'Password cannot be blank.',
            })

        # Check for required fields
        first = request.POST['first-name']
        last = request.POST['last-name']
        email = request.POST['email']
        phone = request.POST['phone']
        emergency_first = request.POST['emergency-first-name']
        emergency_last = request.POST['emergency-last-name']
        emergency_email = request.POST['emergency-email']
        emergency_phone = request.POST['emergency-phone']
        # accept_terms = request.POST['accept-terms']
        accept_terms = request.POST.get('accept-terms', '') == 'on'

        # TO DO:  Refactor:  move this to a separate function with different scenarios?
        if first == '' or last == '' or email == '' or phone == '' or emergency_first == '' or emergency_last == '' or emergency_email == '' or emergency_phone == '':
            return render(request, 'enrollment/register.html', {
                'message': 'You must enter all required fields.',
            })

        if accept_terms != True:
            # if accept_terms != 'Yes':
            return render(request, 'enrollment/register.html', {
                'message': 'You must accept the class policies.',
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first
            user.last_name = last
            user.phone = phone
            user.emergency_first = emergency_first
            user.emergency_last = emergency_last
            user.emergency_email = emergency_email
            user.emergency_phone = emergency_phone
            if accept_terms == 'Yes':
                user.accept_terms = datetime.datetime.now()
            user.save()
        except IntegrityError:
            return render(request, 'enrollment/register.html', {
                'message': 'Username already taken.',
            })
        except Exception:
            return render(request, 'enrollment/register.html', {
                'message': 'Something else went wrong.',
            })
        login(request, user)
        # TO DO:  GO TO THE NEW URL, NOT RENDER
        return view_profile(request, user.id)
    else:
        return render(request, 'enrollment/register.html')


# NAVIGATION

def index(request, page=None, message=None):
    # TO DO:  Consider sort order:  custom?  core/non-core?
    offerings = Offering.objects.filter(semester=latest_semester()).order_by(
        'course__title', 'weekday', 'start_time')
    page = paginate_offerings(request, offerings)
    return render(request, 'enrollment/index.html', {
        'page': page,
        'message': message
    })


@login_required
def view_profile(request, id):
    # Non-admin users may only view their own profiles
    if request.user.id == id or request.user.is_staff:
        try:
            profile = User.objects.get(id=id)
        except User.DoesNotExist:
            return render(request, 'enrollment/profile.html', {
                'orders': None,
                'message': f'User {id} not found.'
            })

        # Prepare the items to pass to the Django template:
        # CITATION:  Passing nested context items:  https://stackoverflow.com/q/6540032

        # Pass the students' completed enrollments, grouped by semester
        # Find all semesters in which the student has completed enrollments
        semesters = Semester.objects.filter(offerings__line_items__order__student=id).order_by('-start_date')
        for semester in semesters:
            semester.enrollments = LineItem.objects.filter(order__student=id).filter(offering__semester=semester).exclude(order__completed=None)
        
        # Pass the order history, including nested line items
        orders = completed_orders(request, id).order_by('-completed')
        for order in orders:
            order.items = order.line_items.all()
        
        return render(request, 'enrollment/profile.html', {
            'orders': orders,
            'semesters': semesters,
            'profile': profile
        })
    else:
        return render(request, 'enrollment/profile.html', {
            'orders': None,
            'message': 'You may not view other users\' profiles'
        })


# UTILITY

# Returns the latest semester that is not in hidden mode
def latest_semester():
    try:
        semester = Semester.objects.filter(hide=False).latest('start_date')
    except Semester.DoesNotExist:
        return None
    return semester


def paginate_offerings(request, offerings):
    # CITATION:  Adapted from Vancara example project in Vlad's section
    # Make sure there are posts before we try to paginate them
    if offerings is None:
        page = None
    else:
        page_num = request.GET.get('page', 1)
        paginator = Paginator(offerings, settings.PAGE_SIZE)
        page = paginator.page(page_num)
    return page

# All completed orders for a given user

def completed_orders(request, user):
    try:
        orders = Order.objects.filter(student=user).exclude(completed=None)
    except Order.DoesNotExist:
        return None
    return orders

# API
