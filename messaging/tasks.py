#!/usr/bin/env python3
"""Tasks description module."""
import json
import datetime
from django_coralline_images.models import UserImage
import docker

from at_logging import build_log
from messaging.app import APP

CLIENT = docker.APIClient(base_url='unix://var/run/docker.sock')


def save_to_database(user_id, tag_image):
    """Saves user image to database. """

    def tag_in_repotags(image):
        return image["RepoTags"][0] == tag_image

    images = CLIENT.images()
    image_item = list(filter(tag_in_repotags, images))[0]

    image_id = image_item["Id"]
    created = datetime.datetime.fromtimestamp(image_item["Created"])
    size = image_item["Size"]

    user_image = UserImage(user_id=user_id,
                           image_id=image_id,
                           tag=tag_image,
                           created=created,
                           size=size
                          )
    user_image.save()


@APP.task
def build_image(user_id, **kwargs):
    """Builds docker image with specified parameters."""

    build_log.write('Started building an image...')
    build_log.write("USER_ID: {}".format(user_id))

    url = "{}.git".format(kwargs["url_address"])
    lines = []

    tag_image = kwargs["tag_image"].lower()
    # docker.errors.APIError: 500 Server Error:
    # Internal Server Error ("invalid reference format:
    # repository name must be lowercase")

    for line in CLIENT.build(path=url, rm=True, tag=tag_image):
        line_str = list(json.loads(line).values())[0]
        lines.append(line_str)

        build_image.update_state(state='PROGRESS',
                                 meta={'line': lines,
                                       'method': kwargs['method']}
                                )

        build_log.write(line_str)

    save_to_database(user_id, tag_image)
