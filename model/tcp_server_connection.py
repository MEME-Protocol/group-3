from socket import timeout
from struct import error
from threading import Event, Lock, Thread

from util.common import create_logger, json_size_struct
from util.registrar import Registrar


class TcpServerConnection(Thread):
    log = create_logger("tcp_connection_logger")

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
            self.log.error("Could not unpack json size")
            exit(0)
            return
        except timeout:
            self.log.error("Received timeout")
            return

        self.log.info(f"Trying to receive and unpack {size}b of json data")
        json_buffer = self.connection.recv(size).decode("utf-8")
        self.log.info(f"Received: {json_buffer}")

        Registrar.deregister_thread(self)
