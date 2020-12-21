from dataclasses import dataclass
from threading import Lock, Thread

from model.user_list import UserList, User
from model.broadcast import Broadcast
from util.common import json_size_struct
from util.common import create_logger

@dataclass
class IncomingBroadcast:
    message: str

@dataclass
class NewUser:
    user: User

@dataclass
class UserLoggedOut:
    user: User

"""Handles incoming message in the order that they are received.
Should handle everything from the udp and tcp ports."""
class InputActor(Thread):
    def __init__(self, local_user: User, outgoing_tcp_connection):
        super().__init__()
        self.log = create_logger("InputActor", client=True)
        self.messages = []
        self.messages_lock = Lock()
        self.users = []
        self.users_lock = Lock()
        self.daemon = True
        self.local_user = local_user
        self.outgoing_tcp_connection = outgoing_tcp_connection
        # todo: Add outgoing udp connection

    def run(self):
        while True:
            command = input("Command: ").strip()
            if command == "messages":
                self.list_messages()
            elif command == "help":
                print("Helpful help message")
            elif command == "users":
                for user in self.get_users():
                    print(f"{user.nickname}: at {user.ip}:{user.port}")
            elif command == "broadcast":
                self.handle_broadcast_request()
            elif command == "message":
                self.handle_direct_message()
            else:
                print("I don't know this command")

    def list_messages(self):
        for message in self.get_messages():
            if type(message) is IncomingBroadcast:
                print(f"Broadcast: {message.message}")
            else:
                print(f"{message.user_name}: {message.message}")


    def handle_direct_message(self):
        receiver = input("Who do you want to message: ")
        user = [user for user in self.users if user.nickname == receiver]
        if len(user) < 1:
            print(f"There is no user with the name {receiver}")
            return
        else:
            user = user[0]
        # todo:
        print(f"Sending message to {user.ip}:{user.port}")

    def handle_broadcast_request(self):
        message = input("Type in your message: ")
        broadcast = Broadcast(message).to_json().encode("utf-8")
        broadcast_length = json_size_struct.pack(len(broadcast))

        self.log.info(f"Broadcasting {broadcast_length + broadcast}")
        self.outgoing_tcp_connection.sendall(broadcast_length + broadcast)

    def tell(self, message):
        self.log.debug(f"Recieved message {message}")
        message_type = type(message)
        if message_type == IncomingBroadcast:
            self.messages_lock.acquire()
            self.messages.append(message)
            self.messages_lock.release()
        elif message_type == NewUser:
            self.users_lock.acquire()
            if message.user != self.local_user:
                self.users.append(message.user)
            self.users_lock.release()
        elif message_type == UserLoggedOut:
            self.users_lock.acquire()
            self.users.remove(message.user)
            self.users_lock.release()
        else:
            self.log.warn(f"Could not handle message {message}")

    def get_users(self):
        self.users_lock.acquire()
        users = self.users
        self.users_lock.release()
        return users

    def get_messages(self):
        self.messages_lock.acquire()
        message = self.messages
        self.messages = []
        self.messages_lock.release()
        return message
