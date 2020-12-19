from threading import Thread, Lock, Event
from socket import timeout
from util.registrar import Registrar
from struct import Struct, error

class TcpServerConnection(Thread):
    def __init__(self, connection):
        super().__init__()
        self.daemon = True
        self.connection = connection
        # u32
        self.json_size_struct = Struct("I")

        Registrar.register_thread(self)

    def run(self):
        while not Registrar.shutdown_requested():
            try:
                size = self.json_size_struct.unpack(self.connection.recv(4))
            except error:
                print("Could not unpack json size")
                continue
            except timeout:
                print("Recieved timeout")
                continue

            json_buffer = self.connection.recv(size)
            while (buffer_size := len(json_buffer)) < size:
                # todo: does this work / is this necessary ?
                json_buffer += self.connection.recv(size - buffer_size)

            print(json_buffer.decode("utf-8"))

        Registrar.deregister_thread(self)
