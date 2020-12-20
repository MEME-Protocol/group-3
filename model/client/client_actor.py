from dataclasses import dataclass
from threading import Lock, Thread

from model.user_list import UserList
from util.common import create_logger


@dataclass
class IncomingMessage:
    user_name: str
    message: str

@dataclass
class UserUpdate:
    user_list: UserList

"""Handles incoming message in the order that they are received.
Should handle everything from the udp and tcp ports."""
class ClientActor(Thread):
    def __init__(self):
        super().__init__()
        self.log = create_logger("ClientActor")
        self.messages = []
        self.messages_lock = Lock()
        self.daemon = True

    def run(self):
        while True:
            self.messages_lock.acquire()
            if len(self.messages) > 0:
                self.messages_lock.release()
                self.handle_next_message()
                continue
            self.messages_lock.release()

    def tell(self, message):
        self.log.debug(f"Recieved message {message}")

        self.messages_lock.acquire()
        self.messages.append(message)
        self.messages_lock.release()

    def get_next_message(self):
        self.messages_lock.acquire()
        message = self.messages.pop()
        self.messages_lock.release()
        return message

    def handle_next_message(self):
        message = self.get_next_message()
        message_type = type(message)
        if message_type == IncomingMessage:
            self.log.info(f"Incoming message from {message.user_name}: {message.message}")
        elif message_type == UserUpdate:
            self.log.info(f"Added ({message.user_list})")
        else:
            self.log.warn(f"Cannot handle messages of type ({message_type})")
