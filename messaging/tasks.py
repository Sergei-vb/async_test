"""Tasks description module."""
import random
import json

import docker

from celery import Celery

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

    if kwargs["tag_image"] == "default":
        kwargs["tag_image"] = "default{}".format(random.randint(1, 100000))

    url = "{}.git".format(kwargs["url_address"])

    lines = []

    for line in CLIENT.build(path=url, rm=True, tag=kwargs["tag_image"]):

        line_str = list(json.loads(line).values())[0]

        build_log.write(line_str)

        lines.append(line_str)
        build_image.update_state(state='PROGRESS',
                                 meta={'line': lines,
                                       'method': kwargs['method']}
                                )
