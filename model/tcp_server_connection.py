from threading import Thread, Lock, Event
from socket import timeout
from util.registrar import Registrar
from util.common import json_size_struct
from struct import Struct, error

class TcpServerConnection(Thread):
    def __init__(self, connection):
        super().__init__()
        self.daemon = True
        self.connection = connection

        Registrar.register_thread(self)

    def run(self):
        try:
            buffer = self.connection.recv(4)
            size = json_size_struct.unpack(buffer)[0]
        except error:
            print("Could not unpack json size")
            exit(0)
            return
        except timeout:
            print("Received timeout")
            return

        print(f"Trying to receive and unpack {size}b of json data")
        json_buffer = self.connection.recv(size).decode("utf-8")
        print(f"Received: {json_buffer}")

        Registrar.deregister_thread(self)
