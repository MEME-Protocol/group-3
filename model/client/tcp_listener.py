import socket
import struct
from threading import Thread

from model.broadcast import Broadcast
from model.client.input_actor import (
    IncomingBroadcast,
    InputActor,
    NewUser,
    UserLoggedOut,
)
from model.user_list import UserList
from util.common import create_logger, json_size_struct

"""Handles listening on the tcp port. Messages on this ports are server-side
messages when a user registers or de-registers"""


class TcpListener(Thread):
    def __init__(self, connection, intput_actor: InputActor):
        super().__init__()
        self.daemon = True
        self.log = create_logger("TcpListener", client=True)

        self.connection = connection
        self.intput_actor = intput_actor

    def run(self):
        while True:
            if not (json_size := self.receive_json_size()):
                self.log.info("Server dropped connection, stopping Thread")
                return

            message = self.connection.recv(json_size).decode("utf-8")
            message = self.parse_message(message)

            self.share_message(message)

    def receive_json_size(self):
        while True:
            try:
                json_size_buffer = self.connection.recv(4)
                if len(json_size_buffer) == 0:
                    return None
                return json_size_struct.unpack(json_size_buffer)[0]
            except socket.error:
                self.log.debug("Timeout listening for packages")
            except struct.error:
                self.log.warn(f"Parsing error, cannot parse {json_size_buffer} to u32")

    def share_message(self, parsed_message):
        if type(parsed_message) is UserList:
            for user in parsed_message.users.added:
                self.intput_actor.tell(NewUser(user))
            for user in parsed_message.users.removed:
                self.intput_actor.tell(UserLoggedOut(user))
        elif type(parsed_message) is Broadcast:
            self.intput_actor.tell(IncomingBroadcast(parsed_message.message))
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
