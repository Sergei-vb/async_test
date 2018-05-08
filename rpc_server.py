#!/usr/bin/env python3
"""Back-end logic. """
import json
import logging
import re
import os

import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import tornado.gen

from tornado.concurrent import run_on_executor, futures

from c_messaging import tasks
from c_messaging.app import APP as celery_app
from c_rpc_base.websocket import SecWebSocket
from c_rpc_base import CLIENT


def make_app():
    """Routing."""
    return tornado.web.Application([
        (r"/load_from_docker/", DockerWebSocket),
    ])


class DockerWebSocket(SecWebSocket):
    """WebSocket handler, implementing Docker RPC. """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.receiver = None
        self.executor = futures.ThreadPoolExecutor(max_workers=4)
        self.start_monitor()

    @run_on_executor
    def monitor(self, app):

        def show_progress(event):
            if event.get('info', None):
                line = event['info'].get('line', None)
                method = event['info'].get('method', None)
                self.build_output(line, method)

        def show_failed(event):
            if event.get('info', None):
                line = event['info'].get('line', None)
                method = event['info'].get('method', None)
                self.build_output(line, method)

        with app.connection() as connection:
            print('connected to celery')

            self.receiver = app.events.Receiver(connection, handlers={
                'task-progress-{}'.format(self.user_id): show_progress,
                'task-failed-{}'.format(self.user_id): show_failed,
            })
            self.receiver.capture(limit=None, timeout=None, wakeup=True)

    @tornado.gen.coroutine
    def start_monitor(self):
        yield self.monitor(celery_app)

    def _get_user_images(self):
        db_images = tasks.UserImage.objects.filter(
            user_id=self.user_id
        ).values().exclude(tag='')
        all_images = CLIENT.images(quiet=True)

        return [{'tag': i['tag'],
                 'available': True if i['image_id'] in all_images else False}
                for i in db_images]

    def _build_image(self, **kwargs):
        tasks.build_image.delay(self.user_id, **kwargs)

        self.write_message({
            "result": "Building image...",
            "error": None,
            "method": kwargs["method"]
        })

    def _images(self, **kwargs):
        user_images = self._get_user_images()

        self.write_message({
            "result": user_images,
            "error": None,
            "method": kwargs["method"]
        })

    def _containers(self, **kwargs):
        data_list = []

        for i in CLIENT.containers(all=True, filters={"label": "out"}):
            data_list.append((i["Names"][0], i["Status"]))

        self.write_message({
            "result": data_list,
            "error": None,
            "method": kwargs["method"]
        })

    def _create(self, **kwargs):
        CLIENT.create_container(image=kwargs["params"]["elem"], labels=["out"])
        self._containers(**kwargs)

    def _start(self, **kwargs):
        CLIENT.start(container=kwargs["params"]["elem"])
        self._containers(**kwargs)

    def _stop(self, **kwargs):
        CLIENT.stop(container=kwargs["params"]["elem"], timeout=0)
        self._containers(**kwargs)

    def _remove(self, **kwargs):
        CLIENT.remove_container(container=kwargs["params"]["elem"])
        self._containers(**kwargs)

    def on_message(self, message):
        data = json.loads(message)

        general = {
            "build_image": self._build_image,
            "images": self._images,
            "containers": self._containers,
            "create": self._create,
            "start": self._start,
            "stop": self._stop,
            "remove": self._remove
        }

        if data["method"] == "build_image":
            ready = self.check_ready_for_build(**data)
            if ready:
                general[data["method"]](**data)

        elif data["method"] in general.keys():
            general[data["method"]](**data)

        else:
            self.write_message({
                "result": None,
                "error": "Client error",
                "method": "error"
            })

    def check_ready_for_build(self, **kwargs):
        """
        Checks compliance with all conditions for build
        and then returns answer about ready.
        """
        reg = re.compile(
            (r"\d+/[a-z\d]"
             r"((?:([a-z\d-])|([.])(?!\3)|([_])(?![_]{2,})){,242}[a-z\d])?"
             r":[\w][\w.-]{,127}"),
            re.ASCII
        )
        if not kwargs["params"]["tag_image"]:
            self.write_message({
                "result": None,
                "error": "You need to specify a tag for the image!",
                "method": "error"
            })

        elif tasks.UserImage.objects.filter(tag=kwargs["params"]["tag_image"]):
            self.write_message({
                "result": None,
                "error": "This tag already exists. Choose another!",
                "method": "error"
            })

        elif not reg.match(kwargs["params"]["tag_image"]):

            # Rules for creating an image tag:
            # https://docs.docker.com/engine/reference/commandline/tag/
            self.write_message({
                "result": None,
                "error": ("Name components may contain lowercase letters, "
                          "digits and separators. A separator is defined "
                          "as a period, one or two underscores, or one or "
                          "more dashes. A name component may not start "
                          "or end with a separator.\n"
                          "A tag name must be valid ASCII and may "
                          "contain lowercase and uppercase letters, "
                          "digits, underscores, periods and dashes. "
                          "A tag name may not start with a period or "
                          "a dash and may contain a maximum of "
                          "128 characters."),
                "method": "error"
            })

        else:
            return True

        return False

    def build_output(self, line, method):
        """Translate the output results of building docker images
        to the client. """

        self.write_message({
            "result": line,
            "error": None,
            "method": method,
        })


if os.getenv("TEST"):
    import tests.mock_celery as tasks
    from tests.mock_docker import MockClientDockerAPI

    CLIENT = MockClientDockerAPI()
    APP = make_app()

if __name__ == "__main__":
    tornado.options.parse_command_line()
    APP = make_app()

    if os.getenv("PORT"):
        logging.info("Use your PORT: %s", os.getenv("PORT"))
    else:
        logging.info("Use default PORT: 8889")
    APP.listen(os.getenv("PORT", 8889))
    tornado.ioloop.IOLoop.current().start()
