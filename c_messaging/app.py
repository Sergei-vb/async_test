"""Create an instance of Celery. """
from celery import Celery


APP = Celery(
    'tasks',
    backend='rpc://',
    broker='amqp://',
    include=['c_messaging.tasks']
)
