"""
Django settings for dance_school project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# CITATION:  Why and how to hide SECRET_KEY in Django https://www.youtube.com/watch?v=Nxa8wkELqJA
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'enrollment',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dance_school.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # CITATION: https://chriskief.com/2013/09/19/access-django-constants-from-settings-py-in-a-template/
                'enrollment.context_processors.global_settings'
            ],
        },
    },
]

WSGI_APPLICATION = 'dance_school.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'enrollment.User'

WEEKDAYS = (
       (0, 'Monday'),
       (1, 'Tuesday'),
       (2, 'Wednesday'),
       (3, 'Thursday'),
       (4, 'Friday'),
       (5, 'Saturday'),
       (6, 'Sunday'),
   )

# Fields allowed to be edited by the profile update form

EDITABLE_USER_FIELDS = [
    'first_name',
    'last_name',
    'email',
    'phone',
    'emergency_first',
    'emergency_last',
    'emergency_email',
    'emergency_phone'
]

# TO DO:  Replace this with a more realistic size
PAGE_SIZE = 5

# ENTER YOUR SCHOOL'S CUSTOMIZATIONS HERE:
# NOTE:  These must also be added to context_processors.py to be used by Django templates and/or JavaScript

# System's default display timezone 
# DEFAULT_TIMEZONE = 'America/New_York'
DEFAULT_TIMEZONE = 'America/Chicago'

# Date and time format
DATE_TIME_FORMAT = 'F jS \\a\\t P'

# Date and time format with timezone 
DATE_TIME_TIMEZONE_FORMAT = 'F jS \\a\\t P T'

# The name of your school
SCHOOL_NAME = 'Belly Dance Somerville'

# The name of your class policies
SCHOOL_POLICIES = 'the Belly Dance Somerville Policies and Community Agreement'

# The text to be displayed if no offerings are found
NO_OFFERINGS = 'Check back soon for information on our upcoming classes.'

# Provide a link to the Markdown cheat sheet below fields that support Markdown formatting in Django admin
# NOTE:  to add this support to additional fields in the future, add this to the field's help_text attribute  
MARKDOWN_HELP_TEXT = 'You may use <a href="https://www.markdownguide.org/cheat-sheet/" target="_blank">Markdown</a> to format this field.'

