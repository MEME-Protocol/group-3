from dataclasses import dataclass
from threading import Lock, Thread

from model.user_list import UserList, User
from util.common import create_logger


@dataclass
class IncomingMessage:
    user_name: str
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
    def __init__(self, local_user: User):
        super().__init__()
        self.log = create_logger("InputActor", client=True)
        self.messages = []
        self.messages_lock = Lock()
        self.users = []
        self.users_lock = Lock()
        self.daemon = True
        self.local_user = local_user

    def run(self):
        while True:
            command = input("Command: ").strip()
            if command == "messages":
                for message in self.get_messages():
                    print(f"{message.user_name}: {message.message}")
            elif command == "help":
                print("Helpful help message")
            elif command == "users":
                for user in self.get_users():
                    print(user.nickname)

    def tell(self, message):
        self.log.debug(f"Recieved message {message}")
        message_type = type(message)
        if message_type == IncomingMessage:
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
