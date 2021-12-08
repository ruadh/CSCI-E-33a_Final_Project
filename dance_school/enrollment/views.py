from django.contrib.auth.decorators import login_required
# from django.http.request import HttpRequest
# from django.http.response import HttpResponse
# import datetime
from datetime import datetime
from django.http.response import HttpResponse
import pytz
from django import forms
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

from .models import GiftCard, Offering, Order, User, Semester, Location, Course, LineItem


# FORM CLASSES

class GiftCardForm(forms.Form):
    card_number = forms.CharField(required=True, strip=True)
    month = forms.CharField(required=True, strip=True)
    year = forms.CharField(required=True, strip=True)
    pin = forms.CharField(required=True, strip=True, label='PIN')
    total = forms.DecimalField(max_digits=6, decimal_places=2, required=True, widget=forms.HiddenInput)

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

    # Pass the latest semester to the template
    semester = latest_semester()

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
    # See if the user is already registered for this offering
    reg = LineItem.objects.filter(order__student=user, offering=offering)
    if reg.exclude(order__completed=None).aggregate(Count('id'))['id__count']:
        error = f'You are already registered for {offering.course.title} in {offering.semester}.'
    # See if this offering is already in the user's cart
    elif action == 'add' and reg.aggregate(Count('id'))['id__count'] > 0:
        error = f'{offering.course.title} is already in your cart.'
    # Make sure we're in the registration period (also enforced by UI)
    elif offering.semester.registration_open > datetime.now(timezone.utc):
        error = f'Registration for {offering.semester} is not yet open.'
    elif offering.semester.registration_close < datetime.now(timezone.utc):
        error = f'Registration is already closed for {offering.semester}.'
    # Make sure space is still available in the class
    elif offering.spots_left < 1:
        error = f'This offering is full.'
    else:
        return None
    return error



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
        validation = validate_item(offering, request.user, 'add')
        # TO DO:  FIX ME HERE
        if validation != None:
            # return validation
            return JsonResponse({'error': validation}, status=400)

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
            return JsonResponse({'error': 'You may not delete line items belonging to another user.'}, status=401)
    else:
        return JsonResponse({'error': 'POST request required'}, status=400)


# Validate the cart and remove any invalid items
@login_required
# TO DO:  ADD CSRF HANDLING
@csrf_exempt
def checkout_validate(request, id):
    try:
        cart = Order.objects.get(pk=id)
    except Order.DoesNotExist:
        return f'Order {id} not found'

    # Restrict checkout to the cart's owner
    if cart.student != request.user:
        return 'You are not authorized to check out carts belonging to another user.'

    # Make sure we're not trying to check out an order that has already been completed (ex: via URL)
    if cart.completed != None:
        return 'This cart has already been checked out.'

    # Make sure the cart is not empty
    try:
        line_items = LineItem.objects.filter(order=id)
    except LineItem.DoesNotExist:
        return f'Cart {cart.id} is empty.'
    
    # Validate each line item again, removing any invalid items from the cart
    removed_list = []
    for line_item in line_items:
        error = validate_item(line_item.offering, cart.student, 'checkout')
        if error != None:
            # Track a list of items and errors for the message
            removed_list.append(f'{line_item.offering.course.title}: {error}')
            # Also remove it from the cart
            line_item.delete()

    # Return a list of any items that have been removed from the cart
    removed_ct = len(removed_list)
    if removed_ct > 0:
        removed_list_delimited = '\n'.join(removed_list)
        return f'{removed_ct} item{"" if removed_ct == 1 else "s"} removed from cart: \n{removed_list_delimited}'

    return None


# Validate payment
@login_required
@csrf_exempt
def validate_payment(request):
    if request.method == 'POST':
        form = GiftCardForm(request.POST)
        if form.is_valid():
            try: 
                # TO DO:  Validate the rest of the details
                card = GiftCard.objects.get(card_number=form.cleaned_data['card_number'], month=form.cleaned_data['month'], year=form.cleaned_data['year'], pin=form.cleaned_data['pin'])
            except GiftCard.DoesNotExist:
                return False

            # Check that the gift card balance is enough to cover the cart total
            total = form.cleaned_data['total']
            if card.amount < total:
                return False
            else:
                card.amount -= total
                card.save()
                return True


# Preview the cart before checkout
@login_required
@csrf_exempt
def checkout_preview(request, id):
    
    # Validate the cart
    message = checkout_validate(request, id)
 
    # Get the cart as an object
    try:
        cart = Order.objects.get(pk=id)
    except Order.DoesNotExist:
        cart = None

    # Double-check that this is the cart's owner
    if cart.student == request.user:

        # Grab the line items
        if cart:
            cart.items = cart.line_items.all()

        # If we're posting, validate payment and submit the order
        if request.method == 'POST':
            paid = validate_payment(request)
            if paid:
                cart.completed = datetime.now(timezone.utc)
                cart.save()
                payment_form = None
                message = 'Thank you for your order.' 
            else:
                message = 'Payment not valid.  Please try again.'
                payment_form = GiftCardForm(initial={'total': cart.total})

        # Otherwise, load the cart preview with a blank payment form
        else:
            payment_form = GiftCardForm(initial={'total': cart.total})

    else:
        payment_form = None
        cart = None

    return render(request, 'enrollment/cart.html', {
            'cart': cart,
            'message': message,
            'semester': latest_semester(),
            'payment_form': payment_form
        })
