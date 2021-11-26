from django.http.request import HttpRequest
from django.http.response import HttpResponse
import datetime
import pytz
# from django.db import models
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django import forms

from .models import User

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
                'timezones': timezones,
                'default_timezone': settings.DEFAULT_TIMEZONE
            })
        if password == '':
            messages.error(request, 'Password cannot be blank')
            return render(request, 'enrollment/register.html', {
                'timezones': timezones,
                'default_timezone': settings.DEFAULT_TIMEZONE
            })

        # TO DO:  Check for required fields
        first = request.POST['first-name']
        last = request.POST['last-name']
        email = request.POST['email']
        phone = request.POST['phone']
        emergency_first = request.POST['emergency-first-name']
        emergency_last = request.POST['emergency-last-name']
        emergency_email = request.POST['emergency-email']
        emergency_phone = request.POST['emergency-phone']
        accept_terms = request.POST['accept-terms']

        if accept_terms != 'Yes':
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
        view_profile(request, user.id)
    else:
        return render(request, 'enrollment/register.html')



# NAVIGATION

def index(request):
    # return HttpResponse('Dance school app!')
    return render(request, 'enrollment/index.html')


def view_profile(request, id):
    return render(request, 'enrollment/profile.html')
