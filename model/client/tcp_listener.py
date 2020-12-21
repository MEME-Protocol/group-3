import socket
import struct
from threading import Thread

from model.client.client_actor import UserUpdate
from model.client.input_actor import IncomingMessage
from model.user_list import UserList
from model.broadcast import Broadcast
from util.common import create_logger, json_size_struct


"""Handles listening on the tcp port. Messages on this ports are server-side
messages when a user registers or de-registers"""
class TcpListener(Thread):
    def __init__(self, connection, client_actor):
        super().__init__()
        self.connection = connection
        self.daemon = True
        self.log = create_logger("TcpListener", client=True)
        self.client_actor = client_actor

    def run(self):
        while True:
            try:
                json_size_buffer = self.connection.recv(4)
                if len(json_size_buffer) == 0:
                    self.log.info("Server dropped connection, stopping Thread")
                    break
                json_size = json_size_struct.unpack(json_size_buffer)[0]
            except socket.error:
                self.log.debug("Timeout listening for packages")
                continue
            except struct.error:
                self.log.warn(f"Parsing error, cannot parse {json_size_buffer} to u32")
                continue

            message = self.connection.recv(json_size).decode("utf-8")
            message = self.parse_message(message)

            if type(message) is UserList:
                self.client_actor.tell(UserUpdate(message))
            elif type(message) is Broadcast:
                self.client_actor.tell(IncomingMessage("broadcast", message.message))
            else:
                self.log.error("Could not parse message")

    def parse_message(self, message):
        parsed_command = None
        try:
            parsed_command = UserList.from_json(message)
        except (KeyError, ValueError):
            self.log.debug("Command could not be parsed as Unregister command")
        try:
            parsed_command = Broadcast.from_json(message)
        except (KeyError, ValueError):
            self.log.debug("Command could not be parsed as Broadcast command")
        return parsed_command
