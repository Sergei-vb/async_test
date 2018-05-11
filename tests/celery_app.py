#!/usr/bin/env python3
"""Mock App Celery. """


# pylint: disable=too-few-public-methods
class Receiver:
    """Processes and stores data for tests. """
    data = []
    check = []

    def __init__(self, _connection=None, handlers=None):
        if handlers:
            handlers = {k: v.__name__ for k, v in handlers.items()}
            self.data.append(handlers)

    def data_from_celery(self, receive_data, info=None):
        """
        Gets data from mock_celery then compares it with data from
        rpc_server and forms array for tests.
        """
        for row in self.data[0].keys():
            if row == receive_data:
                dict_for_check = {self.data[0][row]: {"info": info}}
                self.check.append(dict_for_check)

    @staticmethod
    def capture(limit=None, timeout=None, wakeup=True):
        pass


class EventsMock:
    """Needs only for correct work. """
    # pylint: disable=invalid-name
    @staticmethod
    def Receiver(connection, handlers):
        return Receiver(connection, handlers)


class Broker:
    """Needs only for correct work. """
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CeleryMock:
    """Needs only for correct work. """
    @staticmethod
    def connection():
        """Mock connects to broker. """
        return Broker()

    events = EventsMock()


APP = CeleryMock()
