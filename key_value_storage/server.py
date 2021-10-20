import socket
import asyncio
from collections import defaultdict
from copy import deepcopy


class ServerDriverError(ValueError):
    pass


class Storage:
    """Class for metrics storing"""

    def __init__(self):
        self._data = defaultdict(dict)

    def put(self, key, value, timestamp):
        self._data[key][timestamp] = value

    def get(self, key):

        if key == '*':
            return deepcopy(self._data)

        if key in self._data:
            return {key: deepcopy(self._data.get(key))}

        return {}


class StorageDriver:
    """An interface for storage using"""

    def __init__(self, storage_obj):
        self.storage = storage_obj

    def manage_processing(self, data):
        response = "ok\n"
        data = data.split(" ")
        if data[0] == "put" and len(data) == 4:

            _, key, value, timestamp = data
            value, timestamp = float(value), int(timestamp.strip("\\n\r\n"))
            self.storage.put(key, value, timestamp)
            return response
        elif data[0] == "get" and len(data) == 2:

            _, key = data
            key = key.strip("\\n\r\n")
            key_data = self.storage.get(key)
            for key, value in key_data.items():
                response += "\n".join(f'{key} {value} {timestamp}'
                                      for timestamp, value in sorted(value.items()))
                response += "\n"

            return response
        else:
            raise ServerDriverError()


class MetricsStorageServer:
    loop = asyncio.get_event_loop()

    storage = Storage()
    error_cmd = "error\nwrong_command\n\n"
    ok_cmd = "ok\n"
    separator = "\n"

    def __init__(self, host, port):
        self.driver = StorageDriver(self.storage)

        self.socket = self.__server_setup(host, port)
        self.__loop_setup()

    async def accept_client(self):
        while True:
            user, addr = await self.loop.sock_accept(self.socket)
            print(f"Connection with user {addr[0]}")
            self.loop.create_task(self.receive_data(user))

    async def receive_data(self, user_socket):
        while True:
            try:
                data = await self.loop.sock_recv(user_socket, 4096)

                response = self.driver.manage_processing(data.decode()) + self.separator

            except ServerDriverError:
                response = self.error_cmd

            await self.send_data(user_socket, response)

    async def send_data(self, user_socket, data):
        await self.loop.sock_sendall(user_socket, data.encode("utf-8"))

    async def main(self):
        accept_task = self.loop.create_task(self.accept_client())

        await asyncio.gather(

            accept_task,

        )
        self.loop.close()
        self.socket.close()

    def __loop_setup(self):
        self.loop.run_until_complete(self.main())

    @staticmethod
    def __server_setup(host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen()
        sock.setblocking(False)
        print("Server is ready for work!\n")
        return sock


if __name__ == '__main__':
    server = MetricsStorageServer("127.0.0.1", 10000)
