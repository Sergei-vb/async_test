#!/usr/bin/env python3
"""The module that performs Back-end logic."""
import json
import logging
import re
import os

import docker
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

from messaging import tasks
from at_websocket.websocket import SecWebSocket

CLIENT = docker.APIClient(base_url='unix://var/run/docker.sock')


class TasksManager:
    """A class that manages tasks callbacks."""
    callbacks = dict()

    def register(self, task, callback):
        """Adds new pair 'task-callback' to the callbacks poll."""
        self.callbacks[task] = callback

    def notify_callbacks(self):
        """Rises callbacks in poll."""
        for task, callback in self.callbacks.items():
            if task.state == 'PROGRESS':
                callback(task.info['line'], task.info['method'])


def make_app():
    """Routing."""
    return tornado.web.Application([
        (r"/load_from_docker/", DockerWebSocket),
    ])


class DockerWebSocket(SecWebSocket):
    """The class creates a basic WebSocket handler."""

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.build_lines_count = 0

    def _get_user_images(self):
        db_images = tasks.UserImage.objects.filter(
            user_id=self.user_id
        ).values().exclude(tag='')
        all_images = CLIENT.images(quiet=True)

        return [{'tag': i['tag'],
                 'available': True if i['image_id'] in all_images else False}
                for i in db_images]

    def _url_address(self, **kwargs):
        APP.task_manager.register(
            tasks.build_image.delay(self.user_id, **kwargs),
            self.callback)

        self.write_message(
            dict(
                output='Building image...',
                method=kwargs["method"]
            )
        )

    def _images(self, **kwargs):
        user_images = self._get_user_images()

        self.write_message(
            dict(images=user_images,
                 method=kwargs["method"])
        )

    def _containers(self, **kwargs):
        self.write_message(dict(
            containers=[(i["Names"][0], i["Status"])
                        for i in CLIENT.containers(all=True,
                                                   filters={"label": "out"})],
            method=kwargs["method"]))

    def _create(self, **kwargs):
        CLIENT.create_container(image=kwargs["elem"], command='/bin/sleep 999',
                                labels=["out"])
        self._containers(**kwargs)

    def _start(self, **kwargs):
        CLIENT.start(container=kwargs["elem"])
        self._containers(**kwargs)

    def _stop(self, **kwargs):
        CLIENT.stop(container=kwargs["elem"], timeout=0)
        self._containers(**kwargs)

    def _remove(self, **kwargs):
        CLIENT.remove_container(container=kwargs["elem"])
        self._containers(**kwargs)

    def on_message(self, message):
        data = json.loads(message)
        general = dict(url_address=self._url_address, images=self._images,
                       containers=self._containers, create=self._create,
                       start=self._start, stop=self._stop, remove=self._remove)

        if data["method"] == "url_address":
            ready = self.check_ready_for_build(**data)
            if ready:
                general[data["method"]](**data)

        elif data["method"] in general.keys():
            general[data["method"]](**data)

        else:
            self.write_message(
                dict(message="Client error", method=data["method"]))

    def check_ready_for_build(self, **kwargs):
        """
        Checks compliance with all conditions for build
        and then returns answer about ready.
        """
        reg = re.compile(r'\d+/[\w_]{1,1}[\w.-]{0,127}[:][\w.]+', re.ASCII)
        if not kwargs["tag_image"]:
            self.write_message(
                dict(message="You need to specify a tag for the image!",
                     method="error"))
        elif tasks.UserImage.objects.filter(tag=kwargs["tag_image"]):
            self.write_message(
                dict(message="This tag already exists. Choose another!",
                     method="error"))
        elif not reg.findall(kwargs["tag_image"]) or \
                reg.findall(kwargs["tag_image"])[0] != kwargs["tag_image"]:
            # Rules for creating an image tag:
            # https://docs.docker.com/engine/reference/commandline/tag/
            self.write_message(
                dict(message="A tag name must be valid ASCII and may "
                             "contain lowercase and uppercase letters, "
                             "digits, underscores, periods and dashes. "
                             "A tag name may not start with a period or "
                             "a dash and may contain a maximum of "
                             "128 characters.",
                     method="error"))
        else:
            return True

        return False

    def callback(self, lines, method):
        """Translate the output results of building docker images
        to the client."""

        for line in lines[self.build_lines_count:]:
            self.write_message({
                "output": line,
                "method": method,
            })
        self.build_lines_count = len(lines)


if os.getenv("TEST"):
    import tests.mock_celery as tasks
    from tests.mock_docker import MockClientDockerAPI
    CLIENT = MockClientDockerAPI()
    APP = make_app()
    APP.task_manager = TasksManager()


if __name__ == "__main__":
    tornado.options.parse_command_line()
    APP = make_app()

    APP.task_manager = TasksManager()

    PERIODIC_CALLBACK = tornado.ioloop.PeriodicCallback(
        APP.task_manager.notify_callbacks, 1000)
    PERIODIC_CALLBACK.start()

    if os.getenv("PORT"):
        logging.info("Use your PORT: %s", os.getenv("PORT"))
    else:
        logging.info("Use default PORT: 8889")
    APP.listen(os.getenv("PORT", 8889))
    tornado.ioloop.IOLoop.current().start()
