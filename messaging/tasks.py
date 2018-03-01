from celery import Celery

app = Celery('tasks', backend='amqp', broker='amqp://')
