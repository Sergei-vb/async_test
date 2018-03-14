#!/usr/bin/env python3
"""Tasks description module."""
import json

from celery import Celery
import docker

from at_logging import build_log

APP = Celery('tasks',
             backend='rpc://',
             broker='amqp://',
             include=['messaging.tasks']
             )

CLIENT = docker.APIClient(base_url='unix://var/run/docker.sock')


@APP.task
def build_image(**kwargs):
    """Builds docker image with specified parameters."""

    build_log.write('Started building an image...')

    url = "{}.git".format(kwargs["url_address"])
    lines = []
    tag_image = kwargs["tag_image"].lower()

    for line in CLIENT.build(path=url, rm=True, tag=tag_image):
        line_str = list(json.loads(line).values())[0]

        build_log.write(line_str)

        lines.append(line_str)
        build_image.update_state(state='PROGRESS',
                                 meta={'line': lines,
                                       'method': kwargs['method']}
                                 )
