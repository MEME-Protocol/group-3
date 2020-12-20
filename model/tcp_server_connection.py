import socket
from select import select
import struct
from threading import Event, Lock, Thread
from model.unregister import Unregister
from model.register import Register
from model.user_list import UserList

from util.common import create_logger, json_size_struct
from util.registrar import Registrar


class TcpServerConnection(Thread):


    def __init__(self, connection):
        super().__init__()
        self.daemon = True
        self.connection = connection
        self.connection.settimeout(2)
        self.log = create_logger(f"tcp-connection-logger-{ Registrar.register_thread() }")

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
                self.log.debug("Socket error/timeout")
                continue

            self.log.debug(f"Trying to receive and unpack {size}b of json data")

            json_buffer = self.connection.recv(size).decode('utf-8')
            self.log.info(f"Received: {self.parse_command(json_buffer)}")

        self.log.info("Connection closed, client disconnected")
        Registrar.deregister_thread()

    def parse_command(self, command: str):
        parsed_command = None
        try:
            parsed_command = Unregister.from_json(command)
        except (KeyError, ValueError):
            self.log.debug("Command could not be parsed as Unregister command")
        try:
            parsed_command = Register.from_json(command)
        except (KeyError, ValueError):
            self.log.debug("Command could not be parsed as Register command")
        return parsed_command
