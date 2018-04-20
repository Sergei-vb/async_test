#!/usr/bin/env python3

import datetime
import random
import time


class MockClientDockerAPI:
    def __init__(self):
        self.images_list = []
        self.containers_list = [{'Image': "alpine:3.7",
                                 'Command': "/bin/sleep 999",
                                 'Labels': {'out': ''},
                                 'State': 'created',
                                 'Created': 1524205394,
                                 'Status': 'Created',
                                 'Names': ["/87541"], }]

    def images(self, _name=None, quiet=False, _all=False, _filters=None):
        res = self.images_list

        if quiet:
            res = [x['Id'] for x in res]

        return res

    def containers(self, quiet=False, all=False, _trunc=False, _latest=False,
                   _since=None, _before=None, _limit=-1, _size=False,
                   filters=None):
        res = self.containers_list

        if filters:
            res = [i for i in res if filters["label"] in i["Labels"].keys()]
        if not all:
            res = [i for i in res if i["State"] == "running"]
        if quiet:
            res = [x['Id'] for x in res]

        return res

    def create_container(self, image, command=None, _hostname=None, _user=None,
                         _detach=False, _stdin_open=False, _tty=False,
                         _ports=None, _environment=None, _volumes=None,
                         _network_disabled=False, _name=None, _entrypoint=None,
                         _working_dir=None, _domainname=None,
                         _host_config=None, _mac_address=None, labels=None,
                         _stop_signal=None, _networking_config=None,
                         _healthcheck=None, _stop_timeout=None, _runtime=None):

        dt_now = datetime.datetime.now()
        time_create = (dt_now - datetime.datetime(1970, 1, 1)).total_seconds()
        labels_dict = {i: "" for i in labels}
        name = "/{0}".format(random.randint(1000, 100000))

        container = {'Image': image, 'Command': command, 'Labels': labels_dict,
                     'State': 'created', 'Created': int(time_create),
                     'Status': 'Created', 'Names': [name], }

        self.containers_list.append(container)

    def start(self, container):
        container = "/" + container
        state = ["created", "exited"]
        for i in self.containers_list:
            if container in i["Names"] and i["State"] in state:
                i["State"] = "running"
                i["Status"] = "Up"

    def stop(self, container, timeout=None):
        container = "/" + container
        timeout = 10 if timeout is None else timeout
        for i in self.containers_list:
            if container in i["Names"] and i["State"] == "running":
                time.sleep(timeout)
                i["State"] = "exited"
                i["Status"] = "Exited"

    def remove_container(self, container, _v=False, _link=False, force=False):
        container = "/" + container
        dict_for_remove = None
        state = ["created", "exited"]
        for i in self.containers_list:
            if container in i["Names"] and force:
                dict_for_remove = i
                break
            elif container in i["Names"] and i["State"] in state:
                dict_for_remove = i
                break
        if dict_for_remove:
            self.containers_list.remove(dict_for_remove)

    # def build(self, path=None, tag=None, _quiet=False, _fileobj=None,
    #           _nocache=False, rm=False, _timeout=None,
    #           _custom_context=False, _encoding=None, _pull=False,
    #           _forcerm=False, _dockerfile=None, _container_limits=None,
    #           _decode=False, _buildargs=None, _gzip=False, _shmsize=None,
    #           _labels=None, _cache_from=None, _target=None, _network_mode=None,
    #           _squash=None, _extra_hosts=None, _platform=None):
    #     pass
    #
    # FOR NOW SKIP
