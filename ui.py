#! /usr/bin/python3.9
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, setdefaulttimeout, socket
from struct import Struct
from threading import Thread
from names import get_first_name

from model.register import Register
from model.unregister import Unregister
from util.common import json_size_struct

def listen_on_connection(connection):
    while True:
        buffer = connection.recv(4096)
        print(buffer)

with socket(AF_INET, SOCK_STREAM) as client_socket:
    tcp_host = "127.0.0.1"
    tcp_port = 2000

    client_socket.connect((tcp_host, tcp_port))
    Thread(target=lambda: listen_on_connection(client_socket), daemon=True).start()

    print("Client connected to server")

    json_register = Register(get_first_name(), "127.0.0.1", 5000).to_json().encode("utf-8")

    client_socket.sendall(json_size_struct.pack(len(json_register)) + json_register)

    client_socket.sendall(json_size_struct.pack(len(" ".encode("utf-8"))) + " ".encode("utf-8"))

    client_socket.sendall(json_size_struct.pack(len("{}".encode("utf-8"))) + "{}".encode("utf-8"))

    client_socket.sendall(
        json_size_struct.pack(len("""{"json": "nein"}""".encode("utf-8"))) + """{"json": "nein"}""".encode("utf-8"))

    # json_unregister = Unregister("torsten").to_json().encode("utf-8")
    # client_socket.sendall(json_size_struct.pack(len(json_unregister)) + json_unregister)

    while True:
        pass
