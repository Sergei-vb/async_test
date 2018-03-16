#!/usr/bin/env python3
"""The module that performs Back-end logic."""
import json
import logging
import os

import docker
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

from messaging import tasks

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


class DockerWebSocket(tornado.websocket.WebSocketHandler):
    """The class creates a basic WebSocket handler."""

    build_lines_count = 0

    def data_received(self, chunk):
        """This is a redefinition of the abstract method."""
        pass

    def open(self, *args, **kwargs):
        logging.info("WebSocket opened")

    def _url_address(self, **kwargs):
        APP.task_manager.register(tasks.build_image.delay(**kwargs),
                                  self.callback)
        self.write_message(
            dict(
                output='Building image...',
                method=kwargs["method"]
            )
        )

    def _images(self, **kwargs):
        self.write_message(dict(
            images=[i["RepoTags"][0] for i in CLIENT.images()],
            method=kwargs["method"]))

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
        if data["method"] == "url_address" and not data["tag_image"]:
            self.write_message(
                dict(message="You need to specify a tag for the image!",
                     method="error"))
        elif data["method"] in general.keys():
            general[data["method"]](**data)
        else:
            self.write_message(
                dict(message="Client error", method=data["method"]))

    def on_close(self):
        logging.info("WebSocket closed")

    def callback(self, lines, method):
        """Translate the output results of building docker images
        to the client."""

        for line_n in range(self.build_lines_count, len(lines)-1):
            self.write_message(
                dict(
                    output=lines[line_n],
                    method=method
                    )
                )
        self.build_lines_count = len(lines)-1


if __name__ == "__main__":
    tornado.options.parse_command_line()
    APP = make_app()

    APP.task_manager = TasksManager()

    PERIODIC_CALLBACK = tornado.ioloop.PeriodicCallback(
        APP.task_manager.notify_callbacks, 3000)
    PERIODIC_CALLBACK.start()

    if os.getenv("PORT"):
        logging.info("Use your PORT: %s", os.getenv("PORT"))
    else:
        logging.info("Use default PORT: 8889")
    APP.listen(os.getenv("PORT", 8889))
    tornado.ioloop.IOLoop.current().start()
