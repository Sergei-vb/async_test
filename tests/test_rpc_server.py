#!/usr/bin/env python3
"""Unit tests module. """

from tornado import gen, websocket
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import gen_test
from tornado.escape import json_decode, json_encode

from rpc_server import CLIENT, APP

from tests.mock_django_orm import UserImage


class TestWebSocket(AsyncHTTPTestCase):
    # pylint: disable=too-many-instance-attributes

    """RPC procedures test."""

    #
    # Private methods
    #

    def _ws_connect(self):
        """Establishes websocket connection on test port. """

        return websocket.websocket_connect(
            'ws://localhost:{}{}'.format(self.get_http_port(), self.request)
        )

    @gen.coroutine
    def _get_response(self, message):
        """Sends message to server and get a response. """

        connection = yield self._ws_connect()

        connection.write_message(
            json_encode(message)
        )
        response = yield connection.read_message()

        return json_decode(response)

    def images_init(self):
        """Initializes images list
        in mock DB and mock docker engine
        by default values. """

        self.user_image = UserImage(
            user_id=self.user_id,
            tag=self.tag_image,
            image_id='sha256:342fea22',
            created=1524229897,
            size=191623983
        )
        self.user_image.save()

        CLIENT.images_list.append(
            {'Containers': -1,
             'Created': 1524229897,
             'Id': 'sha256:342fea22',
             'Labels': None,
             'ParentId': 'sha256:55d98c2',
             'RepoDigests': None,
             'RepoTags': [self.tag_image],
             'SharedSize': -1,
             'Size': 191623983,
             'VirtualSize': 191623983}
        )

    def containers_init(self):
        """Initializes containers list
        in mock docker engine
        by default values. """

        def test_container(name, state, status):
            """Creates test container. """
            return {
                'Image': "alpine:3.7",
                'Command': "/bin/sleep 999",
                'Labels': {'out': ''},
                'State': state,
                'Created': 1524205394,
                'Status': status,
                'Names': ["/" + name]
            }

        state_created = 'created'
        state_running = 'running'

        status_created = 'Created'
        status_up = 'Up 15 minutes'

        self.containers_list = [
            test_container(self.container_to_run,
                           state_created, status_created),
            test_container(self.container_running,
                           state_running, status_up),
            test_container(self.container_to_remove,
                           state_created, status_created),
        ]

        CLIENT.containers_list.extend(self.containers_list)

    #
    # Tests
    #

    # General tests. #

    def setUp(self):
        """Initialize test environment. """
        super().setUp()

        self.user_id = "5"
        self.path = "/load_from_docker"
        self.request = self.path + "/?user_id={}".format(self.user_id)

        self.url = "https://github.com/Sergei-vb/coralline-rpc"
        self.new_tag_image = "{}/new_tag:latest".format(self.user_id)
        self.tag_image = "{}/test_tag:latest".format(self.user_id)

        self.container_new = "test_create"
        self.container_to_run = "test_start"
        self.container_running = "test_running"
        self.container_to_remove = "test_remove"

        self.images_init()
        self.containers_init()

    def get_app(self):
        """Returns Tornado web application for using in tests.
        This is a required part of AsyncHTTPTestCase initialization."""

        app = APP
        return app

    def tearDown(self):
        CLIENT.containers_list.clear()

    # HTTP tests

    def test_root(self):
        """This is very simple test, checking server response. """
        self.skipTest("")
        response = self.fetch('/')
        self.assertEqual(response.code, 404)

    def test_http_connection(self):
        """Checks websocket entrypoint. """
        self.skipTest("")
        response = self.fetch(self.request)
        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, b'Can "Upgrade" only to "WebSocket".')

    # RPC procedures tests. #

    # --- main code needs improvement: add websocket connection message --- #
    @gen_test
    def test_websocket_connection(self):
        """Tests websocket connection. """

        message = {"method": None, "params": {"elem": None}}
        response = yield self._get_response(message)

        self.assertEqual('Client error', response["error"])

    @gen_test
    def test_build_image(self):
        """Tests creating images. """

        message = {
            "method": "build_image",
            "params": {"url": self.url,
                       "tag_image": self.new_tag_image}
        }
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "build_image")
        self.assertEqual(response["result"], "Building image...")

        self.assertIn("value_for_user_{0}".format(self.user_id),
                      APP.task_manager.callbacks.keys())

        user_images = [i["tag"] for i in UserImage.objects.all()]
        self.assertIn(self.new_tag_image, user_images)

        docker_images = [i["RepoTags"][0] for i in CLIENT.images_list]
        self.assertIn(self.new_tag_image, docker_images)

    @gen_test
    def test_tag_image_duplicate(self):
        """Tests case when sending existing image tag. """

        message = {
            "method": "build_image",
            "params": {"url": self.url,
                       "tag_image": self.tag_image}
        }
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "error")

    @gen_test
    def test_images(self):
        """Tests getting images list. """

        message = {"method": "images", "params": {"elem": None}}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "images")
        self.assertIsInstance(response["result"], list)

        images = [i["tag"] for i in response["result"]]

        self.assertIn(self.tag_image, images)

    @gen_test
    def test_containers(self):
        """Tests getting containers list. """

        message = {"method": "containers"}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "containers")
        self.assertIsInstance(response["result"], list)
        self.assertNotEqual(len(response["result"]), 0)

        container_name = "/" + self.container_to_run

        containers = {i[0]: i[1] for i in response["result"]}
        self.assertIn(container_name, containers.keys(),
                      "Container not found")

    @gen_test
    def test_create(self):
        """Tests creating a container. """

        cont_num = len(CLIENT.containers_list)

        message = {"method": "create",
                   "params": {"elem": self.tag_image}}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "create")
        self.assertIsInstance(response["result"], list)
        self.assertEqual(len(response["result"]), cont_num + 1)

    @gen_test
    def test_start(self):
        """Tests starting the container. """

        message = {"method": "start",
                   "params": {"elem": self.container_to_run}}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "start")
        self.assertIsInstance(response["result"], list)

        container_name = "/" + self.container_to_run

        containers = {i[0]: i[1] for i in response["result"]}
        self.assertIn(container_name, containers.keys(),
                      "Container not found")

        find_up_status = containers[container_name].lower().find("up")

        self.assertEqual(find_up_status, 0, "Container is not running")

    @gen_test
    def test_stop(self):
        """Tests stopping the container. """

        message = {"method": "stop",
                   "params": {"elem": self.container_running}}
        response = yield self._get_response(message)

        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "stop")
        self.assertIsInstance(response["result"], list)

        container_name = "/" + self.container_running

        containers = {i[0]: i[1] for i in response["result"]}
        self.assertIn(container_name, containers.keys(),
                      "Container not found")

        find_stop_status = containers[container_name].lower().find("exited")

        self.assertEqual(find_stop_status, 0, "Container has not stopped")

    @gen_test
    def test_remove(self):
        """Tests removing the container. """

        message = {"method": "remove",
                   "params": {"elem": self.container_to_remove}}
        response = yield self._get_response(message)
        self.assertIsInstance(response, dict)
        self.assertEqual(response["method"], "remove")
        self.assertIsInstance(response["result"], list)

        container_name = "/" + self.container_to_remove

        containers = {i[0]: i[1] for i in response["result"]}
        self.assertNotIn(container_name, containers.keys(),
                         "Container has found")
