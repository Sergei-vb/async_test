#!/usr/bin/env python3
import os
import logging
from subprocess import PIPE

import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.options
import tornado.websocket
from tornado.process import Subprocess
import docker


CLIENT = docker.APIClient(base_url='unix://var/run/docker.sock')

SETTINGS = {
    "template_path": os.path.join(os.path.dirname(__file__), "template"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}


class RequestAsync(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        process = Subprocess(["fortune"], stdout=PIPE, stderr=PIPE, shell=True)
        yield process.wait_for_exit()
        out, err = process.stdout.read(), process.stderr.read()
        self.write(out)


class Manage(tornado.web.RequestHandler):
    def get(self):
        self.render("manage.html")


def make_app():
    return tornado.web.Application([
        (r"/fortune/", RequestAsync),
        (r"/manage/", Manage),
        (r"/load_from_docker/", DockerWebSocket),
    ], **SETTINGS)


class DockerWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        logging.info("WebSocket opened")

    def on_message(self, message):
        if message == "images":
            self.write_message(dict(
                images=[i["RepoTags"][0] for i in CLIENT.images()]))
        elif message == "containers":
            self.write_message(dict(
                containers=[i["Names"][0] for i in CLIENT.containers()]))

        else:
            self.write_message(dict(message="Client error"))

    def on_close(self):
        logging.info("WebSocket closed")


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = make_app()
    if os.getenv("PORT"):
        logging.info("Use your PORT: {}".format(os.getenv("PORT")))
    else:
        logging.info("Use default PORT: 8889")
    app.listen(os.getenv("PORT", 8889))
    tornado.ioloop.IOLoop.current().start()
