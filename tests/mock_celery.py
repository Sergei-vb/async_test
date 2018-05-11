#!/usr/bin/env python3
"""Mock Celery for unit tests."""
import datetime

from tests.mock_django_orm import UserImage
from tests.mock_docker import MockClientDockerAPI
from tests.celery_app import Receiver


# pylint: disable=too-few-public-methods
class Build:
    """Builds image."""

    @staticmethod
    def delay(user_id, **kwargs):
        """Imitates method delay Celery."""
        tag_image = kwargs["params"]["tag_image"]
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

        MockClientDockerAPI.images_list.append(
            {'Containers': -1,
             'Created': 1,
             'Id': image_id,
             'Labels': None,
             'ParentId': 'sha256:55d98c2',
             'RepoDigests': None,
             'RepoTags': [tag_image],
             'SharedSize': -1,
             'Size': 191623983,
             'VirtualSize': 191623983}
        )

        build = ["Step 1 : VOLUME /data",
                 "Step 2 : CMD ['/bin/sh']",
                 "Successfully built 2855fc"]

        receiver = Receiver()
        for line_str in build:
            meta = {'line': line_str,
                    'method': kwargs['method']}

            receiver.data_from_celery('task-progress-{}'.format(user_id),
                                      info=meta)


# pylint: disable=invalid-name
build_image = Build()
