#!/usr/bin/env python3
"""This module represents secure websocket connection."""
import logging

import tornado.websocket
from tornado.web import MissingArgumentError


class SecWebSocket(tornado.websocket.WebSocketHandler):
    """Implements authentication."""

    def __init__(self, application, request, **kwargs):
        self.user_id = None
        super().__init__(application, request, **kwargs)

    def get(self, *args, **kwargs):
        try:
            self.user_id = self.get_argument('user_id')
            super().get(*args, **kwargs)
        except MissingArgumentError:
            log_msg = "Need 'user_id' query argument to proceed."
            self.set_status(400, log_msg)
            self.finish(log_msg)
            return

    def open(self, *args, **kwargs):
        logging.info("WebSocket opened")

    def on_message(self, message):
        """This is a redefinition of the abstract method."""
        pass

    def data_received(self, chunk):
        """This is a redefinition of the abstract method."""
        pass

    def on_close(self):
        logging.info("WebSocket closed")
