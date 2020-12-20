from dataclasses import dataclass
from socket import socket

import pykka
from util.common import create_logger

from model.user_list import User, UserList, AddedRemovedUsers


@dataclass
class AddedUser:
    user: User
    connection: socket

@dataclass
class RemovedUser:
    user: User
    connection: socket

class TcpOutgoingActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self.log = create_logger("TcpOutgoingActor")
        self.connections = []

    def on_receive(self, message):
        message_type = type(message)
        if message_type == RemovedUser:
            self.log.info("Removing user from connections")
            self.connections.remove(message.connection)

            self.log.info("Sharing closed connection")
            user_list = UserList(
                [AddedRemovedUsers([], [message.user.nickname])]
            ).to_json().encode("utf-8")

            for connection in self.connections:
                self.log.info("Sending data")
                connection.sendall(user_list)

        elif message_type == AddedUser:
            self.log.info("Sharing new user")
            user_list = UserList(
                [AddedRemovedUsers([message.user], [])]
            ).to_json().encode("utf-8")

            for connection in self.connections:
                self.log.info("Sending data")
                connection.sendall(user_list)

            self.log.info("Adding new connection")
            self.connections.append(message.connection)

        else:
            self.log.error(f"Cannot handle messages of type {type(message)}")