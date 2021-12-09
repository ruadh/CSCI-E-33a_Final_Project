# CSCI-E-33a_Final Project
Harvard Extension School CSCI E-33a "Web Programming with Python and JavaScript" Final Project

## About this project

## What each file does

### .env
Stores the SECRET_KEY for security.  All my own work.

### context_processors.py
Lets me pass values from settings.py to Django templates and/or JS.  All my own work.
CITATION:  Learned approach from https://chriskief.com/2013/09/19/access-django-constants-from-settings-py-in-a-template/

### settings.py
Django configuration.  Mostly standard, except that I added:
1. A context processor so I can pass values in this file to Django templates and/or JS
2. Settings that may vary by dance school, such as the school name, local time zone, default class capacity, etc.

### models.py
The models used in this project.  Substantial changes made.



## DESIGN CHOICES:


### Model choices

#### Weekdays handling
I chose to store weekdays as integers instead of as their names, which will support the date calculation features in the "better" and "best" portions of the proposal.  This requires translating them back into their names when we use them in the UI.  I could have done the opposite: store the text and translate to numbers when that's what's needed.  Either would work fine for my proposal features (I'd be using the int and text versions equally), but storing the integers opens the door to internationalization or changing to day abbreviations (Mon vs. Monday) if desired.

#### Price limits
Realistically, most class fees will be in the hundreds of dollars, and order totals only occasionally exceed $1,000.  However, I set the max_digits on those fields to support line item prices in the tens of thousands of dollars, and purchase prices in the hundreds of thousands of dollars.  It's always wise to have a "fudge factor", and other schools may have premium offerings or pricing models that require higher amounts.  This also leaves room for future enhancemnts, like allowing registrations for multiple students in a single order (such as a parent and child taking class together).

#### Orders' required fields
A new Order object requires only the student's foreign key because an order/cart is empty when first created.


#### Line Items 
The LineItems object represents pending enrollments (still in a shopping cart) and completed enrollments (belonging to a completed order).  I decided to call it "line items" instead of enrollments, because a likely future enhancement would be to also allow students to add non-class products to their carts.

#### TO DO:  MAYBE NOT!!!  Users as Model Forms - UPDATE ME
The provided starter files used HTML form in registration.html.   I decided to switch to model forms so we can take advantage on on-page validation, and so we can easily populate the form for an "update your profile" feature.  

This also lets us control which fields are required on the form level vs. the model level.  A likely future enhancement would be to allow users to create accounts with limited information (basic contact info), but require more information at before they check out (terms & conditions, emergency contact info, etc.)   We can't do that if the fields are required at the model level.

#### Gift cards for payment processing
In my proposal, I said that checkout should:
> Validate "payment" (using a dummy credit card number - no integration or security)

I had originally planned to have the dummy credit card number be a hard-coded value, but instead, I decided to store it in a new table based on a GiftCard model, since this also lays the groundwork for including gift card support in the app.  

Actual gift card handling is out of scope for the final project, so I did NOT implement some things that I would be expected:
* Validation, such as amount > 0, card_number contains only digits
* Tracking the original value vs. current balance
* Recording it as the method of payment for a given order

### Passing the request
A lot of my functions take request as a parameter when it isn't required for the functionality, because it supports @login_required.  ex:  get_cart could doesn't need the request (we could require that the user argument instead of providing a default), but unauthenticated users should not be able to get order data.

### Resisting scope creep
There are some features that I did not include because they are not needed to meet my spec, but that I'd recommend adding to the requirements if I were building this for a client.

#### Stored values
There are some cases where we may want to store values in a model instead of referring to fields in a related model.  For example, course names may change over time, but when a student should see the original name when looking at their enrollment history.  That would require us to store the title in the offering model, but managing when that stored value should and shouldn't be updated is pretty complex.  So I couldn't justify spending time on that before meeting the rest of my spec.


### Unused functionality
I chose to include a few features that are not required for the features in my proposal, but that lay the groundwork for some future enhancements that I already have in mind.  Unlike the items above, these were quick to add.

#### Timezones
The current proposal covers only in-person offerings, which we can assume all happen in the same time zone.  However, I chose to include a timezone field in the User and Offering models because that lets us add support for online offerings in the future (Zoom classes, webinars, etc.), and I had already implemented it in earlier projects.



### Settings

I chose to put school-specific values like the school name in settings.py.  This keeps my code DRY, lets us centralize updates, and makes this app customizeable for other schools.  
A more user-friendly way to handle that would be to create a Settings model so these values can be managed in Django Admin.  This is a likely future enhancement, but it's out
of scope for the final project:  it sounds like a quick addition, but we'd also need to ensure that the table only ever has one record, etc.


### Passing the user

In several functions, I chose to pass the user as a separate parameter instead of using request.user.  This is not needed for the features in my final project spec, but it leaves open the door for some future enhancements where the user we're interested in isn't necessarily the current user.  Ex: allowing a parent to register along with a child, or allowing an admin to view orders in the front end.




## DEPENDENCIES:

1) SECRET_KEY

The Django SECRET_KEY value is stored in dance_school/.env
(To access this, you must install python-dotenv in your virtual environment, although this should be handled by requirements.txt)
If this file was not provided (ex: on GitHub), you will need to create it and enter the following:
SECRET_KEY = 'a-new-secure-string'  
(Replacing 'a-new-secure-string' with the string of your choice.)

Alternatively, if you are not running this in production and not sharing the code, you may replace the line in settings.py:
SECRET_KEY = os.getenv('SECRET_KEY')
with
SECRET_KEY = 'a-new-secure-string'


## CITATIONS:

I added comments in my code with the prefix "CITATION:" for code borrowed from outside sources (stack overflow, blogs, project starter files, section examples, etc.).  I did NOT include citations for code adapted from official documentation (Django, Bootstrap), or when an outside source pointed me in the right direction but the work is primarily my own.


## EVALUATION TIPS:

### Semester dates
Many of my features depend on the semester dates.  I set up some sample semesters with realistic dates, but you may want to change those in Django Admin to see them in action.  (ex:  change the registration open/close dates to see how it prevents students from enrolling outside the registration window.)

### Gift cards
BLAH explain.  One card is set up with $1000.  Add new cards or adjust balance in Django Admin.

### Class capacity validation
BLAH add to cart, then update capacity in Django admin, or check out as another user in another browser
