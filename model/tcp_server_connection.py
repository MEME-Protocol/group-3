import socket
from select import select
import struct
from threading import Event, Lock, Thread

from util.common import create_logger, json_size_struct
from util.registrar import Registrar


class TcpServerConnection(Thread):
    log = create_logger("tcp_connection_logger")

    def __init__(self, connection):
        super().__init__()
        self.daemon = True
        self.connection = connection

        Registrar.register_thread()

    def run(self):
        while not Registrar.shutdown_requested():
            try:
                buffer = self.connection.recv(4)
                if len(buffer) == 0:
                    break
                size = json_size_struct.unpack(buffer)[0]
            except struct.error:
                self.log.error("Could not unpack json size")
                continue
            except socket.error:
                self.log.error("Socket error")
                continue
            except socket.timeout:
                self.log.debug("Received timeout while waiting for package")
                continue

            self.log.debug(f"Trying to receive and unpack {size}b of json data")
            json_buffer = b""

            json_buffer += self.connection.recv(size)

            self.log.info(f"Received: {json_buffer.decode('utf-8')}")

        self.log.info("Connection closed, client disconnected")
        Registrar.deregister_thread()
