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
A new Order object requires only the student's foreign key because other values 

#### Stored values
Offering objects store their course's title and subtitle at the time of creation.  This lets us change course details over time, while still maintaining a link between enrollments and courses and making sure that students' enrollment histories reflect the course details that were true at the time of enrollment.  A consequence of this is that if an admin wants to make changes to a course after creating its current offerings, they'll need to update the offerings manually.  A future enhancement would be to allow them to copy over the changes (or lock them out of making changes while registration is open), but since there is a manual work-around, it's not a high enough priority to include in this project's scope. 

#### TO DO:  MAYBE NOT!!!  Users as Model Forms
The provided starter files used HTML form in registration.html.   I decided to switch to model forms so we can take advantage on on-page validation, and so we can easily populate the form for an "update your profile" feature.  

This also lets us control which fields are required on the form level vs. the model level.  A likely future enhancement would be to allow users to create accounts with limited information (basic contact info), but require more information at before they check out (terms & conditions, emergency contact info, etc.)   We can't do that if the fields are required at the model level.


### Non-required features
I chose to include a few features that are not required for the features in my proposal, but that lay the groundwork for some future enhancements that I already have in mind.

#### User timezones
The current proposal covers only in-person offerings, which we can assume all happen in the same time zone.  However, I chose to include user-specific timezones because:
1. It lets us add support for online offerings in the future (Zoom classes, webinars, etc.), 
2. I already implemented this in earlier projects, so it isn't any extra work.


### Settings

I chose to put school-specific values like the school name in settings.py.  This keeps my code DRY, lets us centralize updates, and makes this app customizeable for other schools.  
A more user-friendly way to handle that would be to create a Settings model so these values can be managed in Django Admin.  This is a likely future enhancement, but it's out
of scope for the final project:  it sounds like a quick addition, but we'd also need to ensure that the table only ever has one record, etc.





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
