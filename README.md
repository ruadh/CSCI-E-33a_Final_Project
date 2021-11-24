# CSCI-E-33a_Final Project
Harvard Extension School CSCI E-33a "Web Programming with Python and JavaScript" Final Project

DEPENDENCIES:

1) SECRET_KEY

The Django SECRET_KEY value is stored in dance_school/.env
To access this, you must install python-dotenv in your virtual environment.
If this file was not provided (ex: on GitHub), you will need to create it and enter the following:
SECRET_KEY = 'a-new-secure-string'  
(Replacing 'a-new-secure-string' with the string of your choice.)

Alternatively, if you are not running this in production and not sharing the code, you may replace the line in settings.py:
SECRET_KEY = os.getenv('SECRET_KEY')
with
SECRET_KEY = 'a-new-secure-string'
