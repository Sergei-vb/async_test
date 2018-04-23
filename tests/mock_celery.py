#!/usr/bin/env python3
import datetime

from rpc_server import TasksManager
from tests.mock_django_orm import UserImage


class MakeApp:
    task_manager = TasksManager()


def build(user_id, **kwargs):
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


def build_image(user_id, **kwargs):
    delay = build(user_id, **kwargs)
    return delay
