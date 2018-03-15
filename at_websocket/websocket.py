#!/usr/bin/env python3
"""This module represents secure websocket connection."""
import logging

import tornado.websocket


class SecWebSocket(tornado.websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        self.user_id = None
        super().__init__(application, request, **kwargs)

    def get(self, *args, **kwargs):
        self.user_id = self.get_argument('user_id')
        super().get(*args, **kwargs)

    def open(self, *args, **kwargs):
        logging.info("WebSocket opened")

    def on_message(self, message):
        super(SecWebSocket, self).on_message(message)

    def data_received(self, chunk):
        """This is a redefinition of the abstract method."""
        pass

    def on_close(self):
        logging.info("WebSocket closed")
