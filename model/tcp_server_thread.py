from threading import Thread, Lock, Event
from socket import socket, SOCK_STREAM, AF_INET, SOCK_DGRAM, timeout
from util.registrar import Registrar
from struct import Struct, error

class TcpServerThread(Thread):
    def __init__(self, host, port):
        super().__init__()
        self.daemon = True
        self.host = host
        self.port = port
        # u32
        self.json_size_struct = Struct("I")

        Registrar.register_thread()

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as tcp_server:
            while not Registrar.shutdown_requested():
                tcp_server.bind((self.host, self.port))
                try:
                    size = self.json_size_struct.unpack(tcp_server.recv(4))
                except error:
                    print("Could not unpack json size")
                    continue
                except timeout:
                    print("Recieved timeout")
                    continue

                json_buffer = tcp_server.recv(size)
                while (buffer_size := len(json_buffer)) < size:
                    # todo: does this work / is this necessary ?
                    json_buffer += tcp_server.recv(size - buffer_size)

                print(json_buffer.decode("utf-8"))
        Registrar.deregister_thread()
