from pykka import ThreadingActor
from dataclasses import dataclass
from socket import timeout
from util.registrar import Registrar
from util.common import create_logger, json_size_struct
from struct import error
from socket import socket

@dataclass
class PoisonPill:
    pass
@dataclass
class NewConnection:
    connection: socket

class TcpServerConnection(ThreadingActor):
    log = create_logger("tcp_connection_logger")

    def __init__(self):
        super().__init__()

    def on_receive(self, message):
        if type(message) is PoisonPill:
            Registrar.deregister_thread()
            self.log.info("Received PoisonPill, unregistered Actor from Registrar")
        elif type(message) is NewConnection:
            self.handle_connection(message.connection)
        else:
            self.log.warn(f"Cannot process messages of type {type(message)}")

    def handle_connection(self, connection):
        try:
            buffer = connection.recv(4)
            size = json_size_struct.unpack(buffer)[0]
        except error:
            self.log.error("Could not unpack json size")
            exit(0)
            return
        except timeout:
            self.log.error("Received timeout")
            return

        self.log.info(f"Trying to receive and unpack {size}b of json data")
        json_buffer = connection.recv(size).decode("utf-8")
        self.log.info(f"Received: {json_buffer}")
