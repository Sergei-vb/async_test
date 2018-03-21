import django
from django.conf import settings
import os
import pymysql

from celery import Celery

pymysql.install_as_MySQLdb()

if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj_settings")
django.setup()

APP = Celery('tasks',
             backend='rpc://',
             broker='amqp://',
             include=['messaging.tasks']
)


