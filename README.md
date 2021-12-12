# CSCI-E-33a_Final Project
Harvard Extension School CSCI E-33a "Web Programming with Python and JavaScript" Final Project

## TO DO:
include a full write-up describing your project, what’s contained in each file you created, why you made certain design decisions, and any other additional information the staff should know about your project.

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
2. Customizations for this application, such as the auth user model, and constants such as the weekday integer/name mappings
3. Settings that may vary by dance school, such as the school name, local time zone, default class capacity, etc.

### models.py
The models used in this project. 

### views.py
Form classes and navigation, API, and utility functions in Python.

### admin.py
Customizations to the Django admin area, which is where most administrator tasks occur.

### enrollment.js
JavaScript for BLAH

### styles.css
This application mostly uses Bootstrap styles.  This file contains a small amount of CSS for adding to or modifying those styles.

### tests.py
My attempts at unit testing.  Currently failing at this.  TO DO:  update me

### TO DO:  TEMPLATES

### register.html
The student (end user) registration form.  This is based on register.html file provided in Project 4, and expanded to include additional user profile fields.



## DESIGN CHOICES:


### Model choices

#### Weekdays handling
I chose to store weekdays as integers instead of as their names, which will support the date calculation features in the "better" and "best" portions of the proposal.  This requires translating them back into their names when we use them in the UI.  I could have done the opposite: store the text and translate to numbers when that's what's needed.  Either would work fine for my proposal features (I'd be using the int and text versions equally), but storing the integers opens the door to internationalization or changing to day abbreviations (Mon vs. Monday) if desired.

#### Price limits
Realistically, most class fees will be in the hundreds of dollars, and order totals only occasionally exceed $1,000.  However, I set the max_digits on those fields to support line item prices in the tens of thousands of dollars, and purchase prices in the hundreds of thousands of dollars.  It's always wise to have a "fudge factor", and other schools may have premium offerings or pricing models that require higher amounts.  This also leaves room for future enhancemnts, like allowing registrations for multiple students in a single order (such as a parent and child taking class together).

#### Schedule comments
Spec says "generate the offering's schedule comments".  I chose to do this as no class dates and separate manual schedule_notes field.

#### Orders' required fields
A new Order object requires only the student's foreign key because an order/cart is empty when first created.


#### Line Items 
The LineItems object represents pending enrollments (still in a shopping cart) and completed enrollments (belonging to a completed order).  I decided to call it "line items" instead of enrollments, because a likely future enhancement would be to also allow students to add non-class products to their carts.

#### Users' required fields

As of my "better" scenario, all profile fields are required at the time of registration, but I decided not to require them at the model level because a likely future enhancement (and one of the "best" features I didn't get to) is to require a smaller set at registration and require the rest before checkout.  So for now, only the core fields are required at the model level, and the requirements are enforced by the registration form and the JS and Python code that handles registration and updating user profiles.

It would also have been a little more elegant to replace the registration form with a model form, specifying which fields are required by widget, but it was faster to expand the form we were provided in earlier projects, and going to back to revise it wasn't a priority, given my spec.


#### Gift cards for payment processing
In my proposal, I said that checkout should:
> Validate "payment" (using a dummy credit card number - no integration or security)

I had originally planned to have the dummy credit card number be a hard-coded value, but instead, I decided to store it in a new table based on a GiftCard model, since this also lays the groundwork for including gift card support in the app.  

Actual gift card handling is out of scope for the final project, so I did NOT implement some things that I would be expected:
* Validation, such as amount > 0, card_number contains only digits
* Tracking the original value vs. current balance
* Recording it as the method of payment for a given order

#### Vacation
I decided to tie vacation dates to a semester because the most natural place to enter this information is in an inline in the semester admin.  

I *think* it may be also be better for querying:  if we are trying to find out if an offering date falls in a vacation, we can limit to vacations belonging to a semester ID, instead of doing date math on all date ranges in the vacation table.  I don't know for sure that that's true, though.


#### Calculating vs. storing offering dates
TO DO:  explain

#### Where to format and parse date lists
Formatting and parsing dates in the template vs. doing it in the back-end and passing the string
TO DO:  technically passing the actual date objects lets us do date-aware stuff.  Not sure about performance, though.  Readability sucks, which is why I passed the string.

### Passing the request
A lot of my functions take request as a parameter when it isn't required for the functionality, because it supports @login_required.  ex:  get_cart could doesn't need the request (we could require that the user argument instead of providing a default), but unauthenticated users should not be able to get order data.


### Cart Validation
I decided to block/remove invalid cart items only when the user is intending to interact with the cart:  adding an item, proceeding to checkout, processing checkout.  I decided NOT to run the validation when loading the cart preview on index.html, since that will often happen when the user is trying to do something else (load the class list, browse to another page, etc.).  So removing items and showing an error message related that isn't related to their intended task would be confusing.


### Profile update form

#### Faux form approach
For the profile update form, I decided to use a faux form approach like the edit post feature in Project 4:  values on the page are replaced with inputs via JavaScript, then the results are submitted for processing via the API.  I chose to do that because:
* Most of my features turned out to be doable just with Django, and I needed somewhere to meet the JS requirement
* Using JS lets me implement the "better" feature of allowing a user to edit their profile during checkout without leaving the shopping cart

#### Not hard-coding the fields to be processed
When the API receives the profile update request (the profile function in views.py with a PUT request), I decided to pull the field names from the passed JSON programmatically, rather than hard-coding the list of fields to be processed.   That keeps the code more compact, reduces the amount of work needed when adding new profile fields, and lets us use the same code to update sub-sets of the user profile in the future (ex: just the emergency contact).  

The downside of that approach is that it opens up the ability to edit ANY user field, which is not secure.  (ex:  It would allow a user to set themselves as staff if they could manipulate the payload.)  To prevent this, fields are checked against an allow list, EDITABLE_USER_FIELDS, in settings.py.  I don't know enough about the Django user model to be sure that this would be good enough in a production setting, but I think it's good enough for a class project.


### HTML choices

#### Bootstrap specialty classes on non-specialty elements
In several places, I applied a Bootstrap specialty class to an element that didn't need the special abilities so that the styling would be consistent.  For example, I applied the accordion class to the class list so I can expand/collapse the class details, but applied it to the shopping cart in the sidebar just so it would have the same padding.  

One downside of this approach is that it would make it harder to target the listings by class in JavaScript, but that isn't needed for this project or any of the future enhancements I brainstormed.  Plus, I can easily be overcome the issue by targeting elements with IDs or more complex selectors.  And if that still didn't meet the need, I could start using SASS for my style sheet and set up a new class that inherits from the Boostrap class.


### Resisting scope creep
There are some features that I did not include because they are not needed to meet my spec, but that I'd recommend adding to the requirements if I were building this for a client.

#### Stored values
There are some cases where we may want to store values in a model instead of referring to fields in a related model.  For example, course names may change over time, but when a student should see the original name when looking at their enrollment history.  That would require us to store the title in the offering model, but managing when that stored value should and shouldn't be updated is pretty complex.  So I couldn't justify spending time on that before meeting the rest of my spec.


### Unused functionality
I chose to include a few features that are not required for the features in my proposal, but that lay the groundwork for some future enhancements that I already have in mind.  Unlike the items above, these were quick to add.

#### Timezones
The current proposal covers only in-person offerings, which we can assume all happen in the same time zone.  However, I chose to include a timezone field in the User and Offering models because that lets us add support for online offerings in the future (Zoom classes, webinars, etc.), and I had already implemented it in earlier projects.

During testing, I noticed that a hard refresh in the browser would deactivate the user's timezone, so I re-activate it in every python function that is accessible through a URL.



### Settings

I chose to put school-specific values like the school name in settings.py.  This keeps my code DRY, lets us centralize updates, and makes this app customizeable for other schools.  
A more user-friendly way to handle that would be to create a Settings model so these values can be managed in Django Admin.  This is a likely future enhancement, but it's out
of scope for the final project:  it sounds like a quick addition, but we'd also need to ensure that the table only ever has one record, etc.


### Passing the user

In several functions, I chose to pass the user as a separate parameter instead of using request.user.  This is not needed for the features in my final project spec, but it leaves open the door for some future enhancements where the user we're interested in isn't necessarily the current user.  Ex: allowing a parent to register along with a child, or allowing an admin to view orders in the front end.


### Reloading page after add/remove from cart in JS
After adding or removing a cart item via JS, I am reloading the page instead of using JS to update the elements on the page.  I would like to do that as a future enhancement, but I think the current behavior is acceptable for now:
* On the class list page, Django pagination ensures that the user remains on the same page of results
* On the cart preview page, we do lose any profile updates in progress and payment info entered, but I think that's reasonable since removing an item basically changes  LEFT OFF HERE


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

I added comments in my code with the prefix "CITATION:" for code borrowed from outside sources like Stack Overflow, blogs, project starter files, section examples, etc.

I did NOT include citations for code adapted from official documentation (Django, Bootstrap), or when an outside source pointed me to a concept but I wrote my own code from scratch.  I also did not re-cite simple things that I cited in earlier projects and have now learned as approaches (ex: ternary operators for pluralization, pagination from Vlad's Vancara example in section), unless I am reusing a substantial amount of code (like the login/logout/register functions from starter files0.


## EVALUATION TIPS:

### Semester dates
Many of my features depend on the semester dates.  I set up some sample semesters with realistic dates, but you may want to change those in Django Admin to see them in action.  (ex:  change the registration open/close dates to see how it prevents students from enrolling outside the registration window.)

### Gift cards
BLAH explain.  One card is set up with $1000.  Add new cards or adjust balance in Django Admin.

### Class capacity validation
BLAH add to cart, then update capacity in Django admin, or check out as another user in another browser


## Admin User Setup Guide
