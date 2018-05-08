#!/usr/bin/env python3
"""Tasks description module. """
import json
import datetime
from django_coralline_images.models import UserImage

from c_messaging.app import APP
from c_logging import APP_LOG
from c_rpc_base import CLIENT


def _save_to_database(user_id, tag_image):
    """Saves user image to database. """

    def tag_in_repotags(image):
        return image["RepoTags"][0] == tag_image

    images = CLIENT.images()
    image_item = list(filter(tag_in_repotags, images))[0]

    image_id = image_item["Id"]
    created = datetime.datetime.fromtimestamp(image_item["Created"])
    size = image_item["Size"]

    user_image = UserImage(
        user_id=user_id,
        image_id=image_id,
        tag=tag_image,
        created=created,
        size=size
    )
    user_image.save()


class CTask(celery.Task):
    def __init__(self):
        self.error_messages = []
        super(CTask, self).__init__()


@APP.task(base=CTask, bind=True)
def build_image(self, user_id, **kwargs):
    """Builds docker image with specified parameters. """

    tag_image = kwargs["params"]["tag_image"]

    APP_LOG.info('Started building an image, tag: %s', tag_image)
    APP_LOG.debug("USER_ID: %s", user_id)

    url = "{}.git".format(kwargs["params"]["url"])
    self.error_messages = []

    for line in CLIENT.build(path=url, rm=True, tag=tag_image):
        build_line = json.loads(line.decode())

        if 'error' in build_line.keys():
            self.error_messages.append(build_line['error'])
            APP_LOG.fatal(build_line['error'])

            meta = {'line': build_line['error'],
                    'method': kwargs['method']}

            self.send_event('task-failed', retry=False, info=meta)

        else:
            line_str = list(build_line.values())[0]
            APP_LOG.debug(line_str)

            meta = {'line': line_str,
                    'method': kwargs['method']}

            self.send_event('task-progress', retry=False, info=meta)

    if not self.error_messages:
        _save_to_database(user_id, tag_image)

        APP_LOG.info('Image %s has built successfully.', tag_image)
    else:
        APP_LOG.fatal('Error building image %s! Error message: "%s"',
                      tag_image,
                      self.error_messages)
