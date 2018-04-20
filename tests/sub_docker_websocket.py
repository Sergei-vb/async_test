#!/usr/bin/env python3

import json
import re

from rpc_server import DockerWebSocket
from tests.mock_docker import MockClientDockerAPI

CLIENT = MockClientDockerAPI()


class SubDockerWebSocket(DockerWebSocket):
    build_lines_count = 0

    # def _get_user_images(self):
    #     db_images = tasks.UserImage.objects.filter(
    #         user_id=self.user_id
    #     ).values().exclude(tag='')
    #     all_images = CLIENT.images(quiet=True)
    #
    #     return [{'tag': i['tag'],
    #              'available': True if i['image_id'] in all_images else False}
    #             for i in db_images]
    # FOR NOW SKIP

    # def _url_address(self, **kwargs):
    #     APP.task_manager.register(
    #         tasks.build_image.delay(self.user_id, **kwargs),
    #         self.callback)
    #
    #     self.write_message(
    #         dict(
    #             output='Building image...',
    #             method=kwargs["method"]
    #         )
    #     )
    # FOR NOW SKIP

    def _images(self, **kwargs):
        # user_images = self._get_user_images() FOR NOW SKIP
        user_images = CLIENT.images(quiet=True)

        self.write_message(
            dict(images=user_images,
                 method=kwargs["method"])
        )

    def _containers(self, **kwargs):
        self.write_message(dict(
            containers=[(i["Names"][0], i["Status"])
                        for i in CLIENT.containers(all=True,
                                                   filters={"label": "out"})],
            method=kwargs["method"]))

    def _create(self, **kwargs):
        CLIENT.create_container(image=kwargs["elem"], command='/bin/sleep 999',
                                labels=["out"])
        self._containers(**kwargs)

    def _start(self, **kwargs):
        CLIENT.start(container=kwargs["elem"])
        self._containers(**kwargs)

    def _stop(self, **kwargs):
        CLIENT.stop(container=kwargs["elem"], timeout=0)
        self._containers(**kwargs)

    def _remove(self, **kwargs):
        CLIENT.remove_container(container=kwargs["elem"])
        self._containers(**kwargs)

    def on_message(self, message):
        data = json.loads(message)
        general = dict(url_address=self._url_address, images=self._images,
                       containers=self._containers, create=self._create,
                       start=self._start, stop=self._stop, remove=self._remove)
        if data["method"] == "url_address":
            reg = re.compile(r'\d+/[\w_]{1,1}[\w.-]{0,127}[:][\w.]+', re.ASCII)
            if not data["tag_image"]:
                self.write_message(
                    dict(message="You need to specify a tag for the image!",
                         method="error"))

            # elif tasks.UserImage.objects.filter(tag=data["tag_image"]):
            #     self.write_message(
            #         dict(message="This tag already exists. Choose another!",
            #              method="error"))
            # FOR NOW SKIP

            elif not reg.findall(data["tag_image"]) or \
                    reg.findall(data["tag_image"])[0] != data["tag_image"]:
                # Rules for creating an image tag:
                # https://docs.docker.com/engine/reference/commandline/tag/
                self.write_message(
                    dict(message="A tag name must be valid ASCII and may "
                                 "contain lowercase and uppercase letters, "
                                 "digits, underscores, periods and dashes. "
                                 "A tag name may not start with a period or "
                                 "a dash and may contain a maximum of "
                                 "128 characters.",
                         method="error"))
            else:
                general[data["method"]](**data)
        elif data["method"] in general.keys():
            general[data["method"]](**data)
        else:
            self.write_message(
                dict(message="Client error", method=data["method"]))

    def callback(self, lines, method):
        """Translate the output results of building docker images
        to the client."""

        for line_n in range(self.build_lines_count, len(lines) - 1):
            self.write_message(
                dict(
                    output=lines[line_n],
                    method=method
                )
            )
        self.build_lines_count = len(lines) - 1
