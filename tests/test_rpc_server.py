from tornado import httpserver, gen, websocket, ioloop, web
from tornado.testing import AsyncTestCase, AsyncHTTPTestCase
from tornado.testing import gen_test, bind_unused_port
from tornado.escape import json_decode, json_encode

from tests.sub_docker_websocket import SubDockerWebSocket


def make_app():
    """Routing."""
    return web.Application([
        (r"/load_from_docker/", SubDockerWebSocket),
    ])


class TestWebSocket(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()
        self.container_name = "87541"
        self.user_id = "5"
        self.path = "/load_from_docker"
        self.request = self.path + "/?user_id={}".format(self.user_id)
        self.url_address = "https://github.com/Sergei-vb/coralline-rpc"
        self.tag_image = "{}/tag_from_test:latest".format(self.user_id)

    def get_app(self):
        app = make_app()
        return app

#
# Private methods
#

    def _ws_connect(self):
        return websocket.websocket_connect(
            'ws://localhost:{}{}'.format(self.get_http_port(), self.request)
        )

    @gen.coroutine
    def _get_response(self, message):
        c = yield self._ws_connect()

        c.write_message(
            json_encode(message)
        )
        response = yield c.read_message()

        return json_decode(response)

#
# Tests
#

    """General tests. """

    def test_root(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 404)

    def test_no_user(self):
        response = self.fetch(self.path)
        self.assertEqual(response.code, 404)

    def test_http_connection(self):
        response = self.fetch(self.request)
        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, b'Can "Upgrade" only to "WebSocket".')

    """RPC procedures tests. """

    """ --- needs improvement --- """
    @gen_test
    def test_websocket_connection(self):
        message = {"method": None, "elem": None}
        response = yield self._get_response(message)

        self.assertEqual('Client error', response["message"])
        # TODO: websocket connection message

    """TODO"""
    @gen_test
    def test_images(self):
        message = {"method": "images", "elem": None}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "images")
        self.assertIsInstance(response["images"], list)

        images = [i["tag"] for i in response["images"]]

        self.assertIn(self.tag_image, images)

    """TODO"""
    @gen_test
    def test_url_address(self):
        message = {"method": "url_address",
                   "url_address": self.url_address,
                   "tag_image": self.tag_image}
        response = yield self._get_response(message)

    """OK"""
    @gen_test
    def test_containers(self):
        message = {"method": "containers"}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "containers")
        self.assertIsInstance(response["containers"], list)
        self.assertNotEqual(len(response["containers"]), 0)

        container_name = "/" + self.container_name

        containers = {i[0]: i[1] for i in response["containers"]}
        self.assertIn(container_name, containers.keys(),
                      "Container not found")

    """TODO"""
    @gen_test
    def test_create(self):
        message = {"method": "create",
                   "elem": "5/tag_from_test:latest"}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "create")
        self.assertIsInstance(response["containers"], list)
        # TODO: check existed tag

    """OK"""
    @gen_test
    def test_start(self):
        message = {"method": "start",
                   "elem": self.container_name}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "start")
        self.assertIsInstance(response["containers"], list)

        container_name = "/" + self.container_name

        containers = {i[0]: i[1] for i in response["containers"]}
        self.assertIn(container_name, containers.keys(),
                      "Container not found")

        find_up_status = containers[container_name].lower().find("up")

        self.assertEqual(find_up_status, 0, "Container is not running")

    """OK"""
    @gen_test
    def test_stop(self):
        message = {"method": "start",
                 "elem": self.container_name}
        response = yield self._get_response(message)

        message = {"method": "stop",
                   "elem": self.container_name}
        response = yield self._get_response(message)
        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "stop")
        self.assertIsInstance(response["containers"], list)

        container_name = "/" + self.container_name

        containers = {i[0]: i[1] for i in response["containers"]}
        self.assertIn(container_name, containers.keys(),
                      "Container not found")

        find_stop_status = containers[container_name].lower().find("exited")

        self.assertEqual(find_stop_status, 0, "Container has not stopped")

    """OK"""
    @gen_test
    def test_remove(self):
        message = {"method": "remove",
                   "elem": self.container_name}
        response = yield self._get_response(message)
        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "remove")
        self.assertIsInstance(response["containers"], list)

        container_name = "/" + self.container_name

        containers = {i[0]: i[1] for i in response["containers"]}
        self.assertNotIn(container_name, containers.keys(),
                         "Container has found")
