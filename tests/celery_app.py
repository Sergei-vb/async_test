#!/usr/bin/env python3


class Receiver:
    data = []
    check = []

    def __init__(self, _connection=None, handlers=None):
        if handlers:
            handlers = {k: v.__name__ for k, v in handlers.items()}
            self.data.append(handlers)

    def data_from_celery(self, receive_data, info=None):
        print("----self.data:", self.data)
        for row in self.data[0].keys():
            print("----row:", row)
            print("----receive_data:", receive_data)
            if row == receive_data:
                dict_for_check = {self.data[0][row]: {"info": info}}
                self.check.append(dict_for_check)

    @staticmethod
    def capture(limit=None, timeout=None, wakeup=True):
        pass


class EventsMock:
    @staticmethod
    def Receiver(connection, handlers):
        return Receiver(connection, handlers)


class Broker:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CeleryMock:
    @staticmethod
    def connection():
        """Connects to broker. """
        return Broker()

    events = EventsMock()


celery_app = CeleryMock()
