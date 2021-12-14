# CSCI-E-33a_Final Project
Harvard Extension School CSCI E-33a "Web Programming with Python and JavaScript" Final Project

## About the Dance School app
This app allows an admin user to set up a catalog of courses in current and future semesters, and allows students to register for courses.  Please see my project proposal for the full list of features.  I completed all of the functionality in the "good" and "better" sections, but not the items in the "best" section.

## Dependencies
The required packages are all included in requirements.txt.  
These are the steps that I needed to take to run my project in a fresh virtual environment
1. pip3 install Django
2. pip3 install -r requirements.txt
3. python manage.py makemigrations
4. python manage.py migrate

## Files

### .env
Stores the SECRET_KEY instead of hard-coding it in settings.py for security.  

### context_processors.py
Lets me pass values from settings.py to Django templates and/or JavaScript.  
CITATION:  I learned this approach from https://chriskief.com/2013/09/19/access-django-constants-from-settings-py-in-a-template/

### settings.py
This contains:
1. Standard Django configuration
2. Customizations for this application, such as the auth user model, and constants such as the weekday integer/name mappings
3. Settings that may vary by dance school, such as the school name, local time zone, default class capacity, etc.  

A future enhancement would be to move the school-specific settings to a settings table, so they can be managed in the Django admin area.  

### models.py
The models used in this project. 

### views.py
Contains the back-end Python code for this project.   Includes form classes, navigation views, API functions, and helper functions.

### admin.py
Customizations to the Django admin area, which is where most administrator tasks occur.

### urls.py
Django's URL to Python function mappings.

### enrollment.js
Contains the front-end JavaScript code for this project.  Focuses on adding/removing items from shopping carts and updating user profiles.

### styles.css
This application mostly uses Bootstrap styles, but this file contains a small amount of CSS for adding to or modifying those styles.

### layout.html
Django template for content shown on every page of the application.  Based on layout.html provided in Project 4, but I also added my own message block, footer, a dummy form to provide a CSRF token to JavaScript code.  Also adds Boostrap JavaScript code.

### index.html
Django template for main page of the application, which contains a paginated list of offerings for the current semester and a shopping cart sidebar.  Responsive layout is 2 columns on larger screens, one column at the Bootstrap "md" breakpoint.

### cart.html
Django template for the checkout preview form and order confirmation screen.  Shows the cart contents and, for carts that have not yet been completed:
* Allows the user to review and edit their personal contact information and emergency contacts without leaving the cart
* Completes the checkout with payment by gift card 
Responsive layout is 2 columns on larger screens, one column at the Bootstrap "md" breakpoint.

### contact-sheet.html
Django template for generating a contact list of all students registered for a particular offering. Responsive layout is 2 columns on larger screens, one column at the Bootstrap "md" breakpoint. 

### login.html
Django template for the login screen.  CITATION:  Copied directly from login.html provided in Project 4.  

### profile.html
Django template for the user profile screen.  Shows and allows the user to edit their personal contact info and emergency contacts.  Also shows their enrollments by semester and order history, if any.  Responsive layout is 2 columns on larger screens, one column at the Bootstrap "md" breakpoint.

### register.html
Django template for the student (end user) registration form.  This is based on register.html provided in Project 4, and expanded to include additional user profile fields.



## DESIGN CHOICES:

### Not prioritizing admin functionality
I decided to build this app because I ran my own dance school for ten years, and never found registration software that met my needs.  I'm approching this project as if I were building the software for myself, not as a product for sale.  With that scenario in mind, I prioritized the quality of the student experience and backend code over the quality of the admin experience.  

For example, I spent a lot of time on the validation applied when adding items to cart or checking out, but only applied the minimum necessary validation when an admin user is setting up semesters and offerings, such as start dates falling before end dates.  

There are many things I would like to do in the future to improve the admin area, particularly:
* Using local time zones in the admin area  (the admin area is displaying times in UTC, which gets confusing, especially when entering class times)
* More validations to prevent errors during setup  (ex:  an offering's start and end dates should both fall on the correct weekday)
* Automatically setting values for convenience, like having a vacation end date default to its start date.

My quality for the admin area were:
* It should be possible for *me* (not an average user) to complete all admin tasks outlined in my spec without undue burden.  Tasks should be completable on a single admin screen where practical.
* The admin interface should prevent catastrophic errors that impact functionality, like start dates falling after end dates
* I am responsible for preventing non-catastrophic issues (like start dates falling on the wrong weekday) and enforcing business rules.  The admin inteface does not need to do that for me (yet).

### Model design choices

#### Line Items 
The LineItems object represents both pending enrollments (still in a shopping cart) and completed enrollments (belonging to a completed order).  I decided to call it "line items" instead of enrollments, because a likely future enhancement would be to also allow students to add non-class products to their carts.  If we do that, we'll need to add additional logic to identidfy which line items are class enrollments vs. product purchases.  

#### Orders' required fields
A new Order object requires only the foreign key to the student because an order/cart is empty when first created.

#### Users' required fields
All profile fields are required at the time of registration, but I decided not to require them at the model level because a likely future enhancement (one of the "best" features I didn't get to) is to require a smaller set of information during registration and not require the rest until checkout.  So for now, only the core fields are required at the model level, and the requirements are enforced by the registration form and the JavaScript and Python code that handles registration and updating user profiles.

It would also have been a little more elegant to replace the registration form with a model form, specifying which fields are required by widget.  However, it was faster to expand the form we were provided in earlier projects, and I decided to prioritize other things.

#### Offering schedule comments
In my proposal, I said that vacation dates would be used to generate the offering's schedule comments.  I chose to implement this by using the vacation dates to create the "no class dates" text, but also provide a separate manual schedule_notes field for more free-form notes.

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

#### Calculating vs. storing values
There are several places where I calculate items as model properties that would probably do better as stored values:
* Offering title and subtitle (copying from Course and storing)
* Offering date list  
* Offering no class dates 
* Offering price

These would be better for performance, and also for keeping historical information (ex: preserving an offering's original title if the course's name is changed later).  However, storing these values also requires that we make sure they are updated when appropriate, and the logic for that can get complicated.  For example, we might want to update a stored offering title if its course changes before registration opens, but not afterward.   

This was too much work for something not required in the spec, but it would be a high priority for a future enhancement.  In the meantime, a best practice is for the admin user to finalize semester's details (dates, offerings, vacations) and not make any further changes after turning off the "hidden" flag on the semester.  (I would't count on that in a product situation, but in the scenario where I'm making this for myself, that's acceptable.)

#### User timezones
The current proposal covers only in-person offerings, which we can assume all happen in the same time zone.  However, I chose to include a timezone field in the User model in case they because that lets us add support for online offerings in the future (Zoom classes, webinars, etc.), and I had already implemented it in earlier projects.  During testing, I noticed that a hard refresh in the browser would deactivate the user's timezone, so I re-activate it in every Python function that is accessible through a URL.

#### Cascading
I chose to protect against cascading deletions for all models.  This helps protect us against accidental deletions that could be hard to recover from, makes sure that we don't accidentally lose line items when merging duplicate shopping carts, and makes sure that sales histories aren't lost if a user is deleted.  

The main trade-off is that test records in the admin area takes more steps, such as deleting line items before deleting their parent orders.  That shouldn't be needed too often in production, but it is a hassle during testing.


### Code choices

### Passing the request
A lot of my functions take request as a parameter when it isn't required for the functionality, because it is needed for functions using the @login_required decorator.  Ex:  get_cart in views.py could doesn't need the request (we could require that the user argument instead of defaulting to request.user), but unauthenticated users should not be able to get order data.

### Passing the user
In several functions, I chose to pass the user as a separate parameter instead of using request.user.  This is not needed for the features in my final project spec, but it leaves open the door for some future enhancements where the user we're interested in isn't necessarily the current user.  Ex: allowing a parent to register along with a child, or allowing an admin to view orders in the front end.

### Swap buttons
swapProfileButtons, the JavaScript function that removes the edit profile button and adds save and cancel buttons (or vice-versa) takes the direction of the swap via the "from" argument.  We could also detect the direction of the swap depending on which buttons are already present on page.  I didn't implement that because it wasn't a high priority, and because we'd have make sure that we checked for unexpected cases, like if both types of buttons were somehow present on the page.  Passing the parameter is a little less elegant, but it's robust.

### Cart Validation
I decided to run the validation that removes or prevents the addition of invalid cart itmes only when the user is intending to interact with the cart:  
* Adding an item
* Proceeding to checkout
* Processing checkout.  
I decided NOT to run that validation when loading the cart preview on index.html, since that will often happen when the user is trying to do something else (load the class list, browse to another page, etc.).  Removing items and showing an error message related that isn't related to their intended task would be confusing.

### Error messaging
Errors are shown to the user in two ways:  persistent messages in a dedicated messages area the Django template, and JavaScript alerts.  These roughly correspond to "big picture" tasks (register, checkout) vs. sub-tasks (add to cart, update profile), so having two methods doesn't feel out of place.

If I had had more time, I would have used a temporary message in the Django template that fades after a few seconds (like I did in Project 4) for smaller task errors, while still using the persistent template messages for the big picture tasks errors.

### Faux form for profile updates
For the profile update form, I decided to use a faux form approach like the edit post feature in Project 4.  Values on the page are replaced with inputs via JavaScript, then the results are submitted for processing via the API.  I chose to do that because:
* Most of my features turned out to be doable just with Django, and I needed somewhere to meet the JavaScript requirement
* Using JavaScript lets the user update their pofile during checkout without leaving the shopping cart

### Dynamic list of profile fields to update
The API function that processes profile update requests ("profile" in views.py with a PUT request) determines which fields to update based on which keys are present in the JavaScriptON object it receives.  That keeps the code more compact than hard-coding the values, reduces the amount of work needed when adding new profile fields, and lets us use the same code to update sub-sets of the user profile in the future (ex: just the emergency contact).  

The downside of that approach is that it opens up the ability to edit ANY user field, which is not secure.  (ex:  It would allow a user to set themselves as staff if they could manipulate the payload.)  To prevent this, fields are checked against an allow list, EDITABLE_USER_FIELDS, in settings.py.  I don't know enough about the Django user model to be sure that this would be good enough to secure this in a production setting, but I think it's good enough for a class project.

### Reloading page after JavaScript add/remove from cart
After adding or removing a cart item via JavaScript, I reload the page.  It would be more elegant to use JavaScript to update the elements on the page, and I would like to do that as a future enhancement.  I decided not to prioritize that because the reload behavior didn't turn out to be too disruptive:
* When adding/removing on the class list page, Django pagination ensures that the user remains on the same page of results
* On the cart preview page, removing an item does remove any profile updates in progress and unsubmitted payment info.  But since removing a cart item changes the terms of the transaction, it doesn't feel unreasonable to have to restart the "review" step of the checkout process.  (Plus, the cart organization encourages the user to remove items before updating their profile or entering payment information.)

So this isn't perfect, but I think it is acceptable for an MVP.

### Bootstrap specialty classes on non-specialty elements
In several places, I applied a Bootstrap specialty class to an element that didn't need the special abilities so that the styling would be consistent.  For example, I applied the accordion class to the shopping cart in the sidebar just so it would have the same padding as the class list, where it is neede to expand/collapse the class details.

One downside of this approach is that it would make it harder to target the listings by class in JavaScript, but that isn't needed for this project or any of the future enhancements I brainstormed.  Plus, I can easily be overcome the issue by targeting elements with IDs or more complex selectors.  And if that still didn't meet the need, I could start using SASS for my style sheet and set up a new class that inherits from the Boostrap class.

### Refactor opportunity:  saveProfile and cancelProfile
If I had had more time, I would have merged the saveProfile and cancelProfile functions in enrollment.js.  Both scripts disable and enable the same buttons, call the same API endpoint (just with different methods), and interact with the same DOM elements.  

I would have liked to do this before submitting my homework, but once I dealt with higher priority tasks, I wasn't confident that I had enough time left to implement and test it thoroughly.  It wasn't worth risking introducing bugs at the last minute.


## Citations

I added comments in my code with the prefix "CITATION:" for code borrowed from outside sources like Stack Overflow, blogs, project starter files, section examples, etc.

I did NOT include citations for code adapted from official documentation (Django, Bootstrap), or when an outside source pointed me to a concept but I wrote my own code from scratch.  I also did not re-cite simple things that I cited in earlier projects and have now learned as approaches (ex: ternary operators for pluralization, pagination from Vlad's Vancara example in section), unless I am reusing a substantial amount of code (like the login/logout/register functions from starter files0.


## Testing 

### Sample data
I am submitting this assigment with realistic sample data based on my former dance school.   This includes:
* A full slate of offerings for Spring 2022
* A hidden semester, Summer 2022, which shows how you can start setting up a future semester before releasing it
* Two previous semesters, Fall 2021 and Summer 2021, with one offering each that should not be included in the current offerings list.

### Enrollment caps
When testing for sold-out classes, you may find it easier to change the enrollment limit of an offering in the admin area, rather than creating a lot of fake orders.

### User accounts
I'm not sure if a new superuser account will give you access to the database and my sample data, so I created an admin account for you:

**Username:**  vladpopil
**Password:**  %&zbZTt@auT8896$ysK4
**Email:**  vlad@cs50.harvard.edu

### Setting up new catalog entries
If you want to set up your own course catalog entries, I recommend following this order:
1. Create the semester (if needed)
2. Create the location (if needed)
3. Create the course (if needed)
4. Create the offering

### Fake orders
You may find it helpful to create fake orders in the admin area, rather than logging in as multiple users and going through the checkout process repeatedly.  This can be done in the Orders section of the admin area, which has an inline for line items.   Just be aware:
* The offerings list here is NOT limited to the current semester
* Line items created here are not validated against enrollment limits, etc.
* The line item will not inherit its price from the course - you'll need to enter a price

There is a gift card already set up that you can use when placing test orders.  You'll find it in the admin area.
