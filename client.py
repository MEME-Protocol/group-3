#! /usr/bin/python3.9
import signal
import sys
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, setdefaulttimeout, socket, gethostname
from struct import Struct
from threading import Thread

from model.client.input_actor import InputActor
from model.client.client_actor import ClientActor
from model.client.tcp_listener import TcpListener
from model.register import Register
from model.unregister import Unregister
from model.user_list import User
from util.common import json_size_struct

user_name = input("What is your nickname: ").strip()
user_port = int(input("What is your favorite port: ").strip())
if user_port < 50000 or user_port > 59999:
    print("The port you choose cannot be used for this application")
    sys.exit(1)

user_ip = input("What is your ip-address (leave empty for 127.0.0.1): ").strip()
if len(user_ip) == 0:
    user_ip = "127.0.0.1"

server_port = 2000
server_host = input("What is the servers ip (leave empty for 127.0.0.1): ").strip()
if len(server_host) == 0:
    server_host = "127.0.0.1"

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_host, server_port))


input_actor = InputActor(User(user_name, user_ip, user_port), client_socket)
input_actor.start()
actor = ClientActor(input_actor)
actor.start()
TcpListener(client_socket, actor).start()

json_register = Register(user_name, user_ip, user_port).to_json().encode("utf-8")
client_socket.sendall(json_size_struct.pack(len(json_register)) + json_register)

def shutdown_hook(sig, frame):
    json_unregister = Unregister(user_name).to_json().encode("utf-8")
    client_socket.sendall(json_size_struct.pack(len(json_unregister)) + json_unregister)
    client_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_hook)
signal.pause()
