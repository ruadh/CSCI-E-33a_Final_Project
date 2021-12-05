from django.contrib.auth.decorators import login_required
# from django.http.request import HttpRequest
# from django.http.response import HttpResponse
# import datetime
from datetime import datetime
from django.http.response import HttpResponse
import pytz
# from django.db import models
from django.conf import settings
# from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError, close_old_connections
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
# from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from markdown2 import Markdown

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

    # Add a paginated list of class offerings
    offerings = Offering.objects.filter(semester=latest_semester()).order_by(
        'course__title', 'weekday', 'start_time'
    )
    page = paginate_offerings(request, offerings)

    # If a logged-in user has an active cart, populate it with their incomplete items
    if request.user.is_authenticated:
        cart = get_cart(request, request.user, False)
        if cart:
            cart.items = cart.line_items.all()
    else:
        cart = None

    # Get the name of the latest semester for display
    semester = latest_semester().name

    return render(request, 'enrollment/index.html', {
        'page': page,
        'cart': cart,
        'message': message,
        'semester': semester
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
        # Find all semesters in which the student has completed orders
        semesters = Semester.objects.filter(
            offerings__line_items__order__student=id, offerings__line_items__order__completed__isnull=False).order_by('-start_date').distinct()
        for semester in semesters:
            semester.enrollments = LineItem.objects.filter(order__student=id).filter(
                offering__semester=semester).exclude(order__completed=None)

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


@login_required
def contact_sheet(request, id):
    # TO DO:  clarify that id is the offering id in the docstring
    # Only available for non-admin users
    if request.user.is_staff:
        try:
            offering = Offering.objects.get(id=id)
        except Offering.DoesNotExist:
            offering = None
            students = None
        try:
            students = User.objects.filter(
                orders__line_items__offering=offering)
        except User.DoesNotExist:
            students = None
        return render(request, 'enrollment/contact-sheet.html', {
            'offering': offering,
            'students': students
        })
    else:
        return render(request, 'enrollment/contact-sheet.html', {
            'offerings': None,
            'message': 'You are not authorized to view this page'
        })

# UTILITY

# Returns the latest semester that is not in hidden mode
# NOTE:  This WILL return the semester after registration is closed.  That's intentional.


def latest_semester():
    try:
        semester = Semester.objects.filter(hide=False).latest('start_date')
    except Semester.DoesNotExist:
        return None
    return semester


def current_offerings(request):
    semester = latest_semester()
    try:
        offerings = Offering.objects.filter(semester=semester)
    except Offering.DoesNotExist:
        return None
    return offerings


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
# NOTE:  the user we're intersted in may not be the requestor

def completed_orders(request, user):
    try:
        orders = Order.objects.filter(student=user).exclude(completed=None)
    except Order.DoesNotExist:
        return None
    return orders


# Get the latest incomplete order for a given user, (i.e., their current cart), or optionally create one
# NOTE:  The UI should enforce no more than one incomplete cart, but if they do, we're only interested in the latest
def get_cart(request, user, add=False):
    try:
        cart = Order.objects.get(student=request.user, completed=None)
    except Order.DoesNotExist:
        # If the user doesn't already have an open cart, create one
        if add == True:
            cart = Order(student=request.user)
            cart.save()
        else:
            cart = None
    return cart


# Validate a line item before adding to cart or checking out
# TO DO:  FINISH COMMENTS
# Action = 'add' or 'checkout'

def validate_item(offering, user, action):
    # Make sure we're in the registration window (also enforced by UI)
    if offering.semester.registration_open > datetime.now(timezone.utc):
        return JsonResponse({'error': f'Registration for {offering.semester} is not yet open.'}, status=400)
    if offering.semester.registration_close < datetime.now(timezone.utc):
        return JsonResponse({'error': f'Registration is already closed for {offering.semester}.'}, status=400)
    # Make sure space is still available in the class
    if offering.spots_left < 1:
        return JsonResponse({'error': 'Sorry, this offering is full.'}, status=400)
    # See if the user is already registered for this offering
    reg = LineItem.objects.filter(order__student=user, offering=offering)
    if reg.exclude(order__completed=None).aggregate(Count('id'))['id__count']:
        return JsonResponse({'error': f'You are already registered for {offering.course.title} in {offering.semester}.'}, status=400)
    if action == 'add':
        # See if this offering is already in the user's cart
        if reg.aggregate(Count('id'))['id__count'] > 0:
            return JsonResponse({'error': f'{offering.course.title} is already in your cart.'}, status=400)
    return True


# API

# Add or remove a line item in the cart
@login_required
# TO DO:  Add CSRF handling
@csrf_exempt
def update_cart(request, id):
    if request.method == 'POST':
        try:
            offering = Offering.objects.get(pk=id)
        except Offering.DoesNotExist:
            return JsonResponse({'error': 'Offering not found'}, status=400)

        # Validate
        eligible = validate_item(offering, request.user, 'add')
        if eligible != True:
            return eligible

        # If the user doesn't already have an open order, create a new one
        cart = get_cart(request, request.user, True)

        # Create the line item record
        line_item = LineItem(
            order=cart,
            offering=offering,
            price=offering.price
        )
        # TO DO: Add support for planned absences, price, etc.
        line_item.save()

        return JsonResponse(line_item.serialize(), status=200)
    elif request.method == 'DELETE':
        try: 
            line_item = LineItem.objects.get(id=id)
        except LineItem.DoesNotExist:
            return JsonResponse({'error': f'Line Item {id} not found'}, status=400)

        # Restrict deletion to the line item's owner or an admin user
        if line_item.order.student.id == request.user.id or request.user.is_staff:
            line_item.delete()
            return JsonResponse({}, status=200)
        else:
            return JsonResponse({'error': 'DEV NOTE: NOT AUTHORIZED'}, status=401)
    else:
        return JsonResponse({'error': 'POST request required'}, status=400)
