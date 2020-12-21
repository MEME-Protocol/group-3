import socket
import struct
from threading import Thread

from model.client.client_actor import UserUpdate
from model.client.input_actor import IncomingBroadcast, IncomingUdpMessage
from model.user_list import UserList
from model.broadcast import Broadcast
from util.common import create_logger, json_size_struct
from model.message import UdpMessage


"""Handles listening on the tcp port. Messages on this ports are server-side
messages when a user registers or de-registers"""
class UdpListener(Thread):
    def __init__(self, connection, client_actor):
        super().__init__()
        self.daemon = True
        self.connection = connection
        self.log = create_logger("UdpListener", client=True)
        self.client_actor = client_actor

    def run(self):
        while True:
            try:
                buffer, sender = self.connection.recvfrom(4096)
                if len(buffer) == 0:
                    self.log.info("Server dropped connection, stopping Thread")
                    break
                json_size = json_size_struct.unpack(buffer[:4])[0]
                self.log.info(f"Json size {json_size}")
            except socket.error:
                self.log.debug("Error listening for packages")
                continue
            except socket.timeout:
                self.log.debug("Timeout listening for packages")
                continue
            except struct.error:
                self.log.warn(f"Parsing error, cannot parse {json_size_buffer} to u32")
                continue

            message = buffer[4:(json_size + 4)]
            self.log.info(f"Received message: {message}")
            message = self.parse_message(message)

            if message:
                self.log.info(f"Received direct message: ({message})")
                self.client_actor.tell(IncomingUdpMessage(sender, message.message))
            else:
                self.log.warn("Could not parse direct message")

    def parse_message(self, message):
        parsed_command = None
        try:
            parsed_command = UdpMessage.from_json(message)
        except (KeyError, ValueError):
            self.log.debug("Command could not be parsed as UdpMessage command")
        return parsed_command
