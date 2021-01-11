from dataclasses import dataclass
from socket import socket
from threading import Lock, Thread
from typing import List

from model.broadcast import Broadcast
from model.user_list import AddedRemovedUsers, User, UserList
from util.common import create_logger, json_size_struct


@dataclass
class AddUser:
    user: User
    connection: socket


@dataclass
class RemoveUser:
    user: User


class TcpOutgoing(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.log = create_logger("TcpOutgoingActor")

        self.connections = {}
        self.messages = []
        self.messages_lock = Lock()

    def run(self):
        while True:
            if (message := self.get_message()):
                self.handle_message(message)

    def tell(self, message):
        self.messages_lock.acquire()
        self.messages.append(message)
        self.messages_lock.release()

    def get_message(self):
        message = None
        self.messages_lock.acquire()
        if len(self.messages) > 0:
            message = self.messages.pop()
        self.messages_lock.release()
        return message

    def handle_message(self, message):
        message_type = type(message)
        if message_type == RemoveUser:
            self.remove_user(message)
        elif message_type == AddUser:
            self.add_user(message)
        elif message_type == Broadcast:
            self.handle_broadcast(message)
        else:
            self.log.error(f"Cannot handle messages of type {type(message)}")

    def handle_broadcast(self, broadcast: Broadcast):
        broadcast = broadcast.to_json().encode("utf-8")
        broadcast_length = json_size_struct.pack(len(broadcast))
        for _, connection in self.connections.items():
            connection.sendall(broadcast_length + broadcast)

    def add_user(self, add_user: AddUser):
        self.log.info("Sharing newly added user to clients")
        self.send_user_list(UserList(AddedRemovedUsers([add_user.user], [])))

        self.log.info("Sharing all clients to new user")
        new_user_message = (
            UserList(AddedRemovedUsers(self.connections.keys(), []))
            .to_json()
            .encode("utf-8")
        )
        add_user.connection.sendall(
            json_size_struct.pack(len(new_user_message)) + new_user_message
        )

        self.connections[add_user.user] = add_user.connection
        self.log.info("Added new user to client-connections")

    def remove_user(self, remove_user: RemoveUser):
        self.log.info("Removing user from client-connections")
        if remove_user.user in self.connections:
            self.connections.pop(remove_user.user)

        self.log.info("Sharing removed user to client-connections")
        self.send_user_list(UserList(AddedRemovedUsers([], [remove_user.user])))

    def send_user_list(self, user_list: UserList):
        user_list_b = user_list.to_json().encode("utf-8")
        user_list_size_b = json_size_struct.pack(len(user_list_b))

        for _, connection in self.connections.items():
            connection.sendall(user_list_size_b + user_list_b)
