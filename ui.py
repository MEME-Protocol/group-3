#! /usr/bin/python3.9
from util.common import json_size_struct
from model.register import Register
from socket import setdefaulttimeout, socket, SOCK_STREAM, AF_INET, SOCK_DGRAM
from struct import Struct

with socket(AF_INET, SOCK_STREAM) as client_socket:
    tcp_host = "127.0.0.1"
    tcp_port = 2000

    client_socket.connect((tcp_host, tcp_port))
    print("Client connected to server")

    json = Register("torsten", "127.0.0.1", 5000).to_json().encode("utf-8")

    client_socket.sendall(json_size_struct.pack(len(json)) + json)
