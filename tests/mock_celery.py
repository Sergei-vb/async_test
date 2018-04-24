#!/usr/bin/env python3
"""Mock Celery for unit tests."""
import datetime

from tests.mock_django_orm import UserImage
from tests.mock_docker import MockClientDockerAPI


# pylint: disable=too-few-public-methods
class Build:
    """Builds image."""

    @staticmethod
    def delay(user_id, **kwargs):
        """Imitates method delay Celery."""
        tag_image = kwargs["tag_image"].lower()
        image_id = "Id:....."
        created = datetime.datetime.now()
        size = 0

        data_format = dict(user_id=user_id,
                           image_id=image_id,
                           tag=tag_image,
                           created=created,
                           size=size)

        user_image = UserImage(**data_format)
        user_image.save()

        MockClientDockerAPI.images_list.append(data_format)

        return "value_for_user_{0}".format(user_id)


# pylint: disable=invalid-name
build_image = Build()
