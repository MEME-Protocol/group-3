from dataclasses import dataclass
from socket import socket
from typing import List

from threading import Thread, Lock
from model.user_list import AddedRemovedUsers, User, UserList
from model.broadcast import Broadcast
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
                self.on_receive(message)

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

    def on_receive(self, message):
        message_type = type(message)
        if message_type == RemoveUser:
            self.log.info("Removing user from connections")
            if message.user in self.connections:
                self.connections.pop(message.user)

            self.log.info("Sharing closed connection")
            user_list = (
                UserList(AddedRemovedUsers([], [message.user]))
                .to_json()
                .encode("utf-8")
            )
            user_list_size = json_size_struct.pack(len(user_list))

            for _, connection in self.connections.items():
                self.log.info("Sending data")
                connection.sendall(user_list_size + user_list)

        elif message_type == AddUser:
            self.log.info("Sharing new user")
            user_list = (
                UserList(AddedRemovedUsers([message.user], []))
                .to_json()
                .encode("utf-8")
            )
            user_list_size = json_size_struct.pack(len(user_list))

            for _, connection in self.connections.items():
                self.log.info("Sending data")
                connection.sendall(user_list_size + user_list)

            # Send user list to new user
            new_user_message = (
                UserList(AddedRemovedUsers(self.connections.keys(), []))
                .to_json()
                .encode("utf-8")
            )
            message.connection.sendall(
                json_size_struct.pack(len(new_user_message)) + new_user_message
            )

            self.log.info("Adding new connection")
            self.connections[message.user] = message.connection

        elif message_type == Broadcast:
            broadcast = message.to_json().encode("utf-8")
            broadcast_length = json_size_struct.pack(len(broadcast))
            for _, connection in self.connections.items():
                connection.sendall(broadcast_length + broadcast)
        else:
            self.log.error(f"Cannot handle messages of type {type(message)}")
