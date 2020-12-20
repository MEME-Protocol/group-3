from threading import Thread
from util.common import create_logger, json_size_struct
import socket
import struct

class TcpListener(Thread):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.daemon = True
        self.log = create_logger("TcpListener")

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
            self.log.info(message)
