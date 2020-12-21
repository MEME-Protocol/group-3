import socket
import struct
from select import select
from threading import Event, Lock, Thread

from util.common import create_logger, json_size_struct
from util.registrar import Registrar

from model.register import Register
from model.unregister import Unregister
from model.user_list import User
from model.broadcast import Broadcast


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
                    self.log.info("Connection closed, client disconnected")
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
            command = self.parse_command(json_buffer)

            if type(command) is Unregister:
                user = Registrar.retrieve_user(command.nickname)
                Registrar.deregister_user(user, self.connection)
                self.log.info(f"Deregistered user {user}")
                self.log.info("Closing connection to client")
                break
            elif type(command) is Register:
                user = User(command.nickname, command.ip, command.port)
                Registrar.register_user(user, self.connection)
                self.log.info(f"Registered user {user}")
            elif type(command) is Broadcast:
                Registrar.broadcast_message(command)
                self.log.warn(f"Broadcasting message: ({command})")
            else:
                self.log.warn(f"Can not execute command {command}")

        self.connection.close()
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
        try:
            parsed_command = Broadcast.from_json(command)
        except (KeyError, ValueError):
            self.log.debug("Command could not be parsed as Broadcast command")
        return parsed_command
