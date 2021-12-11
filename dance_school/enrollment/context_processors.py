from django.conf import settings

# CITATION:  Passing a settings value to Django templates and/or JS from: 
# https://chriskief.com/2013/09/19/access-django-constants-from-settings-py-in-a-template/

def global_settings(request):
    return {
    'DEFAULT_TIMEZONE': settings.DEFAULT_TIMEZONE,
    'TIME_FORMAT': settings.TIME_FORMAT,
    'DATE_TIME_FORMAT': settings.DATE_TIME_FORMAT,
    'DATE_TIME_FORMAT_NO_YEAR': settings.DATE_TIME_FORMAT_NO_YEAR,
    'DATE_TIME_TIMEZONE_FORMAT': settings.DATE_TIME_TIMEZONE_FORMAT,
    'SCHOOL_NAME': settings.SCHOOL_NAME,
    'SCHOOL_POLICIES': settings.SCHOOL_POLICIES,
    'NO_OFFERINGS': settings.NO_OFFERINGS,
    }