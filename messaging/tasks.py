#!/usr/bin/env python3
"""Tasks description module."""
import json

from celery import Celery
import docker

from at_logging import build_log
from models import UserImage

APP = Celery('tasks',
             backend='rpc://',
             broker='amqp://',
             include=['messaging.tasks']
            )

CLIENT = docker.APIClient(base_url='unix://var/run/docker.sock')


@APP.task
def build_image(user_id, **kwargs):
    """Builds docker image with specified parameters."""

    build_log.write('Started building an image...')

    build_log.write("USER_ID: " + user_id)

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
    image_id = list(filter(lambda x: x["RepoTags"][0] == tag_image,
                           CLIENT.images()))[0]["Id"].split(":", 1)[1]
    created = list(filter(lambda x: x["RepoTags"][0] == tag_image,
                           CLIENT.images()))[0]["Created"]
    size = list(filter(lambda x: x["RepoTags"][0] == tag_image,
                           CLIENT.images()))[0]["Size"]
    UserImage.objects.create(
        user_id=user_id, image_id=image_id, created=created, size=size)
