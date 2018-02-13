#!/usr/bin/env python3
import os
from subprocess import PIPE
import logging

import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.gen
from tornado.process import Subprocess
import tornado.options
from tornado.options import parse_command_line

SETTINGS = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "static_handler_args": {"default_filename": "index.htm"}
}


class RequestAsync(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        # http_client = tornado.httpclient.AsyncHTTPClient()
        # response = yield http_client.fetch("https://ya.ru")
        # self.write(html.escape(response.body.decode('utf-8')))
        process = Subprocess(["fortune"], stdout=PIPE, stderr=PIPE, shell=True)
        yield process.wait_for_exit()
        out, err = process.stdout.read(), process.stderr.read()
        self.write(out)


def make_app():
    return tornado.web.Application([
        # (r"/static/", tornado.web.StaticFileHandler),
        (r"/fortune/", RequestAsync)
    ], **SETTINGS)


if __name__ == "__main__":
    parse_command_line()
    app = make_app()
    if os.getenv("PORT"):
        logging.info("Use your PORT: {}".format(os.getenv("PORT")))
    else:
        logging.info("Use default PORT: 8889")
    app.listen(os.getenv("PORT", 8889))
    tornado.ioloop.IOLoop.current().start()
