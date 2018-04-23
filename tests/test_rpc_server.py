from tornado import gen, websocket, web
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import gen_test
from tornado.escape import json_decode, json_encode

from tests.sub_docker_websocket import SubDockerWebSocket, CLIENT


def make_app():
    """Routing."""
    return web.Application([
        (r"/load_from_docker/", SubDockerWebSocket),
    ])


class TestWebSocket(AsyncHTTPTestCase):
    """RPC procedures test."""

#
# Private methods
#

    def _ws_connect(self):
        return websocket.websocket_connect(
            'ws://localhost:{}{}'.format(self.get_http_port(), self.request)
        )

    @gen.coroutine
    def _get_response(self, message):
        connection = yield self._ws_connect()

        connection.write_message(
            json_encode(message)
        )
        response = yield connection.read_message()

        return json_decode(response)

    def images_init(self):
        CLIENT.images_list.append(
            {"tag": self.tag_image, "available": True}
        )

    def containers_init(self):
        containers_list = [{'Image': "alpine:3.7",
                            'Command': "/bin/sleep 999",
                            'Labels': {'out': ''},
                            'State': 'created',
                            'Created': 1524205394,
                            'Status': 'Created',
                            'Names': ["/" + self.container_to_run],
                            },
                           {'Image': "alpine:3.7",
                            'Command': "/bin/sleep 999",
                            'Labels': {'out': ''},
                            'State': 'running',
                            'Created': 1524205394,
                            'Status': 'Up 15 minutes',
                            'Names': ["/" + self.container_running],
                            },
                           {'Image': "alpine:3.7",
                            'Command': "/bin/sleep 999",
                            'Labels': {'out': ''},
                            'State': 'created',
                            'Created': 1524205394,
                            'Status': 'Created',
                            'Names': ["/" + self.container_to_remove],
                            },
                           ]
        CLIENT.containers_list.extend(containers_list)

#
# Tests
#

    # General tests. #

    def setUp(self):
        super().setUp()
        self.user_id = "5"
        self.path = "/load_from_docker"
        self.request = self.path + "/?user_id={}".format(self.user_id)

        self.url_address = "https://github.com/Sergei-vb/coralline-rpc"
        self.new_tag_image = "{}/new_tag:latest".format(self.user_id)
        self.tag_image = "{}/test_tag:latest".format(self.user_id)

        self.container_new = "test_create"
        self.container_to_run = "test_start"
        self.container_running = "test_running"
        self.container_to_remove = "test_remove"

        self.images_init()
        self.containers_init()

    def get_app(self):
        app = make_app()
        return app

    # HTTP tests

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

    # RPC procedures tests. #

    # --- needs improvement: add websocket connection message --- #
    @gen_test
    def test_websocket_connection(self):
        message = {"method": None, "elem": None}
        response = yield self._get_response(message)

        self.assertEqual('Client error', response["message"])

    # TODO
    @gen_test
    def test_url_address(self):
        # message = {"method": "url_address",
        #            "url_address": self.url_address,
        #            "tag_image": self.tag_image}
        # response = yield self._get_response(message)
        pass

    # TODO
    @gen_test
    def test_images(self):
        message = {"method": "images", "elem": None}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "images")
        self.assertIsInstance(response["images"], list)

        images = [i["tag"] for i in response["images"]]

        self.assertIn(self.tag_image, images)

    # OK
    @gen_test
    def test_containers(self):
        message = {"method": "containers"}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "containers")
        self.assertIsInstance(response["containers"], list)
        self.assertNotEqual(len(response["containers"]), 0)

        container_name = "/" + self.container_to_run

        containers = {i[0]: i[1] for i in response["containers"]}
        self.assertIn(container_name, containers.keys(),
                      "Container not found")

    # OK
    @gen_test
    def test_create(self):
        cont_num = len(CLIENT.containers_list)

        message = {"method": "create",
                   "elem": self.tag_image}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "create")
        self.assertIsInstance(response["containers"], list)
        self.assertEqual(len(response["containers"]), cont_num+1)

    # OK
    @gen_test
    def test_start(self):
        message = {"method": "start",
                   "elem": self.container_to_run}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "start")
        self.assertIsInstance(response["containers"], list)

        container_name = "/" + self.container_to_run

        containers = {i[0]: i[1] for i in response["containers"]}
        self.assertIn(container_name, containers.keys(),
                      "Container not found")

        find_up_status = containers[container_name].lower().find("up")

        self.assertEqual(find_up_status, 0, "Container is not running")

    # OK
    @gen_test
    def test_stop(self):
        # First, start a container:
        # message = {"method": "start",
        #            "elem": self.container_running}
        # response = yield self._get_response(message)

        message = {"method": "stop",
                   "elem": self.container_running}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "stop")
        self.assertIsInstance(response["containers"], list)

        container_name = "/" + self.container_running

        containers = {i[0]: i[1] for i in response["containers"]}
        self.assertIn(container_name, containers.keys(),
                      "Container not found")

        find_stop_status = containers[container_name].lower().find("exited")

        self.assertEqual(find_stop_status, 0, "Container has not stopped")

    # OK
    @gen_test
    def test_remove(self):
        message = {"method": "remove",
                   "elem": self.container_to_remove}
        response = yield self._get_response(message)
        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "remove")
        self.assertIsInstance(response["containers"], list)

        container_name = "/" + self.container_to_remove

        containers = {i[0]: i[1] for i in response["containers"]}
        self.assertNotIn(container_name, containers.keys(),
                         "Container has found")
