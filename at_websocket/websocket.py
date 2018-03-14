#!/usr/bin/env python3
"""This module represents secure websocket connection."""
import logging

import tornado.websocket


class SecWebSocket(tornado.websocket.WebSocketHandler):

    def open(self, *args, **kwargs):
        logging.info("WebSocket opened")

    def get(self, *args, **kwargs):
        super().get(*args, **kwargs)

    def data_received(self, chunk):
        """This is a redefinition of the abstract method."""
        pass

    def on_close(self):
        logging.info("WebSocket closed")
