from dataclasses import dataclass
from threading import Lock, Thread

from model.client.input_actor import InputActor, NewUser, UserLoggedOut, IncomingBroadcast
from model.broadcast import Broadcast
from model.user_list import UserList
from util.common import create_logger


@dataclass
class UserUpdate:
    user_list: UserList

"""Handles incoming message in the order that they are received.
Should handle everything from the udp and tcp ports."""
class ClientActor(Thread):
    def __init__(self, input_actor: InputActor):
        super().__init__()
        self.log = create_logger("ClientActor", client=True)
        self.messages = []
        self.messages_lock = Lock()
        self.daemon = True
        self.input_actor = input_actor

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
        if message_type == IncomingBroadcast:
            self.log.info(f"Incoming broadcast: ({message.message})")
            self.input_actor.tell(message)
        elif message_type == UserUpdate:
            self.log.info(f"User update ({message.user_list})")
            added_users = message.user_list.users.added
            removed_users = message.user_list.users.removed
            for user in added_users:
                self.input_actor.tell(NewUser(user))
            for user in removed_users:
                self.input_actor.tell(UserLoggedOut(user))
        elif message_type is Broadcast:
            self.log.info("Received broadcast message")
            self.input_actor.tell(message)
        else:
            self.log.warn(f"Cannot handle messages of type ({message_type})")
