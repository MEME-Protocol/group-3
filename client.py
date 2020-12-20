#! /usr/bin/python3.9
import signal
import sys
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, setdefaulttimeout, socket
from struct import Struct
from threading import Thread

from model.client.input_actor import InputActor
from model.client.client_actor import ClientActor
from model.client.tcp_listener import TcpListener
from model.register import Register
from model.unregister import Unregister
from util.common import json_size_struct

tcp_host = "127.0.0.1"
tcp_port = 2000

user_name = input("What is your nickname: ").strip()
user_port = int(input("What is your favorite port: "))
if user_port < 50000 or user_port > 59999:
    print("The port you choose cannot be used for this application")
    sys.exit(1)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((tcp_host, tcp_port))

input_actor = InputActor()
input_actor.start()
actor = ClientActor(input_actor)
actor.start()
TcpListener(client_socket, actor).start()

json_register = Register(user_name, "127.0.0.1", user_port).to_json().encode("utf-8")
client_socket.sendall(json_size_struct.pack(len(json_register)) + json_register)

def shutdown_hook(sig, frame):
    json_unregister = Unregister(user_name).to_json().encode("utf-8")
    client_socket.sendall(json_size_struct.pack(len(json_unregister)) + json_unregister)
    client_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_hook)
signal.pause()
