#!/usr/bin/env python3
import os
import logging
import json
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
        d = json.loads(message)
        if "url-address" in d:
            url = "{}.git".format(d["url-address"])
            for line in CLIENT.build(path=url, rm=True, tag='hardcode'):
                self.write_message(dict(output=line.decode("utf-8")))
        elif "images" in d:
            self.write_message(dict(
                images=[i["RepoTags"][0] for i in CLIENT.images()]))
        elif "containers" in d:
            self.write_message(dict(
                containers=[i["Names"][0] for i in CLIENT.containers()]))
        elif "run" in d:
            container = CLIENT.create_container(
                image=d["elem"], command='/bin/sleep 9000')
            CLIENT.start(container=container.get("Id"))
        elif "stop" in d:
            container = CLIENT.stop(container=d["elem"])
            CLIENT.remove_container(container=container.get("Id"))
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
