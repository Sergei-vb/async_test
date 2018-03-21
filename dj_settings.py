import os

DEBUG = True

DEFAULT_INDEX_TABLESPACE = ''

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.mysql',
       'NAME': os.getenv('NAME'),
       'USER': os.getenv('USER'),
       'PASSWORD': os.getenv('PASSWORD'),
       'HOST': os.getenv('HOST'),
       'PORT': os.getenv('PORTDB'),
   }
}

SECRET_KEY = 'zzz'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',

    'messaging.tasks',
    'django_coralline_images',
]