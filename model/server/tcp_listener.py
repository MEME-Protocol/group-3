import socket
import struct
from select import select
from threading import Event, Lock, Thread

from model.broadcast import Broadcast
from model.register import Register
from model.server.tcp_outgoing import AddUser, RemoveUser, TcpOutgoing
from model.unregister import Unregister
from model.user_list import User
from util.common import create_logger, json_size_struct


class TcpListener(Thread):
    def __init__(self, connection, tcp_outgoing: TcpOutgoing):
        super().__init__()
        self.daemon = True
        self.connection = connection
        self.log = create_logger("tcp-connection-logger")
        self.user = None
        self.tcp_outgoing = tcp_outgoing

    def run(self):
        while True:
            if not (size := self.receive_json_size()):
                break

            self.log.debug(f"Trying to receive and unpack {size}b of json data")

            json_buffer = self.connection.recv(size).decode("utf-8")
            command = self.parse_command(json_buffer)

            if self.handle_command(command) is Unregister:
                break

        self.log.info("Closing connection to client")
        self.connection.close()

    def handle_command(self, command):
        command_type = type(command)
        if command_type is Register:
            self.user = User(command.nickname, command.ip, command.port)
            self.tcp_outgoing.tell(AddUser(self.user, self.connection))
            self.log.info(f"Registered user {self.user}")

        elif command_type is Unregister:
            self.tcp_outgoing.tell(RemoveUser(self.user))
            self.log.info(f"Deregistered user {self.user}")
            return command_type

        elif command_type is Broadcast:
            self.log.warn(f"Broadcasting message: ({command})")
            self.tcp_outgoing.tell(command)

        else:
            self.log.warn(f"Can not execute command {command_type}")

    def receive_json_size(self):
        while True:
            try:
                buffer = self.connection.recv(4)
                if len(buffer) == 0:
                    self.log.info("Connection closed, client disconnected")
                    break
                return json_size_struct.unpack(buffer)[0]
            except struct.error:
                self.log.error("Could not unpack json size")
                continue
            except socket.error:
                self.log.debug("Socket error/timeout")
                continue
        return None

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
