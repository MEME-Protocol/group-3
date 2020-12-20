#! /usr/bin/python3.9
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, setdefaulttimeout, socket
from struct import Struct
from threading import Thread
from names import get_first_name
import signal
from model.register import Register
from model.unregister import Unregister
from util.common import json_size_struct

def listen_on_connection(connection):
    while True:
        buffer = connection.recv(4096)
        print(buffer)

tcp_host = "127.0.0.1"
tcp_port = 2000

user_name = get_first_name()
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((tcp_host, tcp_port))
Thread(target=lambda: listen_on_connection(client_socket), daemon=True).start()

json_register = Register(user_name, "127.0.0.1", 5000).to_json().encode("utf-8")
client_socket.sendall(json_size_struct.pack(len(json_register)) + json_register)

print(f"Username: {user_name}")

def shutdown_hook(sig, frame):
    json_unregister = Unregister(user_name).to_json().encode("utf-8")
    client_socket.sendall(json_size_struct.pack(len(json_unregister)) + json_unregister)
    client_socket.close()

signal.signal(signal.SIGINT, shutdown_hook)
signal.pause()
