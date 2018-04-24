#!/usr/bin/env python3
import datetime

from tests.mock_django_orm import UserImage


class Build:
    @staticmethod
    def delay(user_id, **kwargs):
        tag_image = kwargs["tag_image"].lower()
        image_id = "Id:....."
        created = datetime.datetime.now()
        size = 0
        user_image = UserImage(
            user_id=user_id,
            image_id=image_id,
            tag=tag_image,
            created=created,
            size=size)
        user_image.save()
        return "value_for_user_{0}".format(user_id)


build_image = Build()
