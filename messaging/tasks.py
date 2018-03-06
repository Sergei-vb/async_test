"""Module Celery."""
from celery import Celery

APP = Celery('tasks', backend='amqp', broker='amqp://')
