#!/usr/bin/env python3
"""Tasks description module."""
import json
import datetime
from django_coralline_images.models import UserImage

from c_messaging.app import APP
from c_logging import APP_LOG
from c_rpc_base import CLIENT


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

    tag_image = kwargs["tag_image"].lower()
    # docker.errors.APIError: 500 Server Error:
    # Internal Server Error ("invalid reference format:
    # repository name must be lowercase")

    APP_LOG.info('Started building an image, tag: %s', tag_image)
    APP_LOG.debug("USER_ID: %s", user_id)

    url = "{}.git".format(kwargs["url_address"])
    lines = []

    for line in CLIENT.build(path=url, rm=True, tag=tag_image):
        line_str = list(json.loads(line).values())[0]
        lines.append(line_str)

        build_image.update_state(state='PROGRESS',
                                 meta={'line': lines,
                                       'method': kwargs['method']}
                                )

        APP_LOG.debug(line_str)

    save_to_database(user_id, tag_image)

    APP_LOG.info('Image %s has built successfully.', tag_image)
