'''Python code for the Enrollment app in Django project Dance School'''

# CITATION:     Import sorting by iSort, as recommended by the Django contributors documentation:
#               https://github.com/PyCQA/isort#readme

import json
from datetime import datetime

import pytz
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import GiftCard, LineItem, Offering, Order, Semester, User


# FORM CLASSES

class GiftCardForm(forms.Form):
    card_number = forms.CharField(required=True, strip=True)
    month = forms.CharField(required=True, strip=True)
    year = forms.CharField(required=True, strip=True)
    pin = forms.CharField(required=True, strip=True, label='PIN')
    total = forms.DecimalField(
        max_digits=6, decimal_places=2, required=True, widget=forms.HiddenInput)


# AUTHENTICATION
# CITATION:  Adapted from provided starter files in earlier projects


def login_view(request):
    '''Log in an existing user'''

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
    '''Log out the current user'''

    logout(request)
    timezone.activate(settings.DEFAULT_TIMEZONE)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    '''Create a new end user (student) account'''

    # Gather a list of timezones to populate the timezone choice field in the form
    timezones = pytz.common_timezones

    if request.method == 'POST':

        # Ensure password matches confirmation
        # NOTE:  I think Django trims whitespace from these, but trim anyway to be safe
        username = request.POST['username'].strip()
        password = request.POST['password'].strip()
        confirmation = request.POST['confirmation'].strip()
        if password != confirmation:
            return render(request, 'enrollment/register.html', {
                'message': 'Passwords must match.',
            })
        if password == '':
            return render(request, 'enrollment/register.html', {
                'message': 'Password cannot be blank.',
            })

        first = request.POST['first-name'].strip()
        last = request.POST['last-name'].strip()
        email = request.POST['email'].strip()
        phone = request.POST['phone'].strip()
        emergency_first = request.POST['emergency-first-name'].strip()
        emergency_last = request.POST['emergency-last-name'].strip()
        emergency_email = request.POST['emergency-email'].strip()
        emergency_phone = request.POST['emergency-phone'].strip()
        accept_terms = request.POST.get('accept-terms', '') == 'on'

        # Check for required fields
        if (first == '' or last == '' or email == '' or phone == '' or emergency_first == '' or emergency_last == ''
                or emergency_email == '' or emergency_phone == ''):
            return render(request, 'enrollment/register.html', {
                'message': 'All fields are required.',
            })

        if accept_terms is not True:
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
        timezone.activate(user.timezone)
        return HttpResponseRedirect(reverse('view_profile', args=[user.id]))
    else:
        timezone.activate(settings.DEFAULT_TIMEZONE)
        return render(request, 'enrollment/register.html')


def set_timezone(request):
    '''Activates the user's preferred timezone if logged in, or the system default.'''
    if request.user.is_authenticated:
        timezone.activate(request.user.timezone)
    else:
        timezone.activate(settings.DEFAULT_TIMEZONE)


# Offerings

def index(request, message=None):
    '''Displays the app's home page with a paginated list of current offerings'''

    # Determine the latest semester
    semester = latest_semester()

    # Add a paginated list of class offerings
    offerings = Offering.objects.filter(semester=semester).order_by(
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

    # Make sure the timezone isn't overriden by a hard reset
    set_timezone(request)
    return render(request, 'enrollment/index.html', {
        'page': page,
        'cart': cart,
        'message': message,
        'semester': semester
    })


def latest_semester():
    '''Returns the latest semester that has not been marked hidden, regardless of whether registration is open.'''

    try:
        semester = Semester.objects.filter(hide=False).latest('start_date')
    except Semester.DoesNotExist:
        return None
    return semester


def current_offerings(request):
    '''Returns all offerings for the current semester'''

    semester = latest_semester()
    try:
        offerings = Offering.objects.filter(semester=semester)
    except Offering.DoesNotExist:
        return None
    return offerings


def paginate_offerings(request, offerings):
    '''Return the first page of a pagainted list of offerings'''

    if offerings is None:
        page = None
    else:
        page_num = request.GET.get('page', 1)
        paginator = Paginator(offerings, settings.PAGE_SIZE)
        page = paginator.page(page_num)
    return page


# PROFILES

@login_required
def profile_view(request, id):
    '''Display the user profile page, if authorized'''

    # Make sure the timezone isn't overridden by a hard reset
    set_timezone(request)

    if request.method == 'GET':
        # Non-admin users may only view their own profiles
        if request.user.id == id or request.user.is_staff:
            try:
                profile = User.objects.get(id=id)
            except User.DoesNotExist:
                return render(request, 'enrollment/profile.html', {
                    'orders': None,
                    'message': f'User {id} not found.'
                })

            # Gather the students' completed enrollments, grouped by semester
            # CITATION:  Passing nested context items:  https://stackoverflow.com/q/6540032
            semesters = Semester.objects.filter(
                offerings__line_items__order__student=id,
                offerings__line_items__order__completed__isnull=False).order_by('-start_date').distinct()
            for semester in semesters:
                semester.enrollments = LineItem.objects.filter(order__student=id).filter(
                    offering__semester=semester).exclude(order__completed=None)

            # Gather their order history, including nested line items
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
    else:
        return render(request, 'enrollment/profile.html', {
            'orders': None,
            'message': 'GET method required'
        })


@login_required
def profile(request, id):
    '''
    Retrieve or update a user's editable profile fields via the API

    Note: The list of editable fields is EDITABLE_USER_FIELDS in settings.py
    '''

    if request.method != 'POST' and request.method != 'GET':
        return JsonResponse({'error': 'GET or POST method required.'}, status=400)
    else:
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)

        # Don't allow non-staff users to edit other's profiles
        if request.user != user and not request.user.is_staff:
            return JsonResponse({'error': 'You are not authorized to access this profile.'}, status=400)

        # If we're posting, make the changes
        if request.method == 'POST':

            # Convert the passed JSON into a Python dictionary
            body = json.loads(request.body)

            # Update each of the fields that were passed, if on the allow list
            for field in body:
                # NOTE: model fields use underscores, while HTML elements use dashes
                field_name = field.replace('-', '_')
                if field_name in settings.EDITABLE_USER_FIELDS:
                    field_value = body.get(field).strip()
                    if field_value == '':
                        return JsonResponse({'error': 'All fields required.'}, status=400)
                    # CITATION: https://www.programiz.com/python-programming/methods/built-in/setattr
                    setattr(user, field_name, field_value)
            user.save()

        # Return the updated profile's editable fields
        return JsonResponse(user.serialize_editable(), status=200)


@login_required
def authorized_get_profile(request, id):
    '''Returns profile object (not page) only if you are its owner or a staff user'''

    # Make sure the profile exists
    try:
        profile = User.objects.get(pk=id)
    except User.DoesNotExist:
        profile = None
    # Return it only if it is being requested by the owner or a staff user
    else:
        if profile != request.user and not request.user.is_staff:
            profile = None
    finally:
        return profile


@login_required
def completed_orders(request, user):
    '''Returns a queryset of completed orders for a given user, who may not be the requestor'''
    try:
        orders = Order.objects.filter(student=user).exclude(completed=None)
    except Order.DoesNotExist:
        return None
    return orders


# CONTACT SHEET

@login_required
def contact_sheet(request, id):
    '''Displays the contact sheet page for a single offering "id" '''

    # Make sure the timezone isn't overriden by a hard reset
    set_timezone(request)

    # Restrict to admin users
    if request.user.is_staff:
        try:
            offering = Offering.objects.get(id=id)
        except Offering.DoesNotExist:
            offering = None
            students = None
        try:
            students = User.objects.filter(
                orders__line_items__offering=offering).order_by('last_name', 'first_name')
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


# CART MANAGEMENT


@login_required
def get_cart(request, user=None, add=False):
    '''
    Returns the latest incomplete order for the specified user.

    Merges duplicates, and optionally creates one if it does not already exist'''

    # Default to the logged-in user
    if user is None:
        user = request.user
    try:
        cart = Order.objects.get(student=user, completed=None)
    except Order.DoesNotExist:
        # If the user doesn't already have an open cart, create one
        if add is True:
            cart = Order(student=user)
            cart.save()
        else:
            cart = None
    except Order.MultipleObjectsReturned:
        cart = merge_carts(request, user)
    return cart


@login_required
def merge_carts(request, user=None):
    '''If a user has multiple open carts, merges them into one'''

    # Default to the requestor
    if user is None:
        user = request.user
    # Only staff can merge other users' carts
    if request.user != user and not request.user.is_staff:
        return None
    # Gather the user's open carts, creating a new one if none found
    try:
        carts = Order.objects.filter(student=user, completed=None)
    except Order.DoesNotExist:
        primary = Order(student=user)
        primary.save()
    if carts.count() > 1:
        # Select a primary cart
        primary = carts.first()
        # Reassign any line items to the first cart
        line_items = LineItem.objects.filter(
            order__student=user, order__completed=None).exclude(order=primary)
        for line_item in line_items:
            line_item.order = primary
            line_item.save()
        # Delete the duplicate carts
        for cart in carts:
            if cart != primary:
                cart.delete()

    return primary


@login_required
def update_cart(request, id):
    '''
    Add or remove a line item from a cart via the API

    Note:  the id argument refers to the offering to add during a POST, but the line item ID during a DELETE
    '''

    if request.method == 'POST':

        # Check the offering
        try:
            offering = Offering.objects.get(pk=id)
        except Offering.DoesNotExist:
            return JsonResponse({'error': 'Offering not found'}, status=400)

        # Validate the item
        validation = validate_item(request, offering, request.user, 'add')
        if validation is not None:
            return JsonResponse({'error': validation}, status=400)

        # If the user doesn't already have an open order, create a new one
        cart = get_cart(request, request.user, True)

        # Create the line item record
        line_item = LineItem(
            order=cart,
            offering=offering,
            price=offering.price
        )
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


@login_required
def validate_item(request, offering, user, action):
    '''
    Validate a line item

    Note: action ("add" or "checkout") controls which validations are applied
    '''
    # See if the user is already registered for this offering
    reg = LineItem.objects.filter(order__student=user, offering=offering)
    if reg.exclude(order__completed=None).aggregate(Count('id'))['id__count']:
        error = f'You are already registered for {offering.course.title} in {offering.semester}.'
    # See if this offering is already in the user's cart (add to cart only)
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


# CHECKOUT

@login_required
def checkout(request, id):
    '''Preview or submit incomplete cart "id", or view a completed order'''

    # Make sure the timezone isn't overriden by a hard reset
    set_timezone(request)

    # Default behavior:  no payment update profile forms
    payment_form = None
    profile = None

    # Get the cart
    try:
        cart = Order.objects.get(pk=id)
        # Grab the line items to pass to the Django template
        if cart:
            cart.items = cart.line_items.all()
    except Order.DoesNotExist:
        cart = None
        message = f'Order {id} not found.'
    else:

        if request.method == 'GET':
            # If the cart isn't completed, validate the items, then load the preview with a payment form and profile
            if cart.completed is None:
                message = validate_checkout(request, id)
                if cart.student != request.user:
                    cart = None
                else:
                    payment_form = GiftCardForm(initial={'total': cart.total})
                    profile = authorized_get_profile(request, cart.student.id)
            # If the cart is completed, check if authorized (since we're not validating) and show the confirmation page
            else:
                payment_form = None
                if cart.student != request.user and not request.user.is_staff:
                    cart = None
                    message = 'You may not view other users\' orders'
                else:
                    message = None
        elif request.method == 'POST':
            # Revalidate the cart, in case it has become invalid since the preview screen was loaded
            message = validate_checkout(request, id)
            if message is None:
                # Validate payment and submit the order
                paid = pay(request)
                if paid:
                    cart.completed = datetime.now(timezone.utc)
                    cart.save()
                    message = 'Thank you for your order.'
                else:
                    payment_form = GiftCardForm(initial={'total': cart.total})
                    profile = authorized_get_profile(request, cart.student.id)
                    message = 'Payment declined.  Please try again.'
            # If someone is trying to post a cart they don't own, don't render the cart or payment form
            elif cart.student != request.user:
                cart = None
            else:
                payment_form = GiftCardForm(initial={'total': cart.total})
                profile = authorized_get_profile(request, cart.student.id)
        else:
            message = 'POST or GET request required.'
    finally:
        return render(request, 'enrollment/cart.html', {
            'cart': cart,
            'message': message,
            'semester': latest_semester(),
            'payment_form': payment_form,
            'profile': profile
        })


@login_required
def validate_checkout(request, id):
    '''Validate order "ID" and remove any invalid items'''

    try:
        cart = Order.objects.get(pk=id)
    except Order.DoesNotExist:
        return f'Order {id} not found'

    # Restrict checkout to the cart's owner
    if cart.student != request.user:
        return 'You are not authorized to access carts belonging to another user.'

    # Make sure we're not trying to check out an order that has already been completed
    if cart.completed is not None:
        return 'This cart has already been checked out.'

    # Make sure the cart is not empty
    try:
        line_items = LineItem.objects.filter(order=id)
    except LineItem.DoesNotExist:
        return f'Cart {cart.id} is empty.'

    # Validate each line item again, removing any invalid items from the cart
    removed_list = []
    for line_item in line_items:
        error = validate_item(request, line_item.offering,
                              cart.student, 'checkout')
        if error is not None:
            # Record the item name and error
            removed_list.append(f'{line_item.offering.course.title}: {error}')
            # Remove the invalid item from the cart
            line_item.delete()

    # Return a list of any items that have been removed from the cart
    removed_ct = len(removed_list)
    if removed_ct > 0:
        removed_list_delimited = '\n'.join(removed_list)
        return f'{removed_ct} item{"" if removed_ct == 1 else "s"} removed from cart: \n{removed_list_delimited}'

    return None


@login_required
def pay(request):
    '''Validate the payment form, and deduct from the gift card balance if successful'''
    if request.method == 'POST':
        form = GiftCardForm(request.POST)
        if form.is_valid():
            try:
                card = GiftCard.objects.get(
                    card_number=form.cleaned_data['card_number'], month=form.cleaned_data['month'],
                    year=form.cleaned_data['year'], pin=form.cleaned_data['pin'])
            except GiftCard.DoesNotExist:
                return False

            # Check that the gift card balance is enough to cover the cart total
            total = form.cleaned_data['total']
            if card.amount < total:
                return False
            else:
                # Deduct the total from the gift card balance
                card.amount -= total
                card.save()
                return True
