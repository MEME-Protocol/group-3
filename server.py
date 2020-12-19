#! /usr/bin/python3.9
import signal
import sys
from threading import Thread
from util.registrar import Registrar
from model.tcp_server_connection import TcpServerConnection
from socket import setdefaulttimeout, socket, SOCK_STREAM, AF_INET, SOCK_DGRAM

def shutdown_hook(sig, frame):
    print("Shutdown requested")
    Registrar.request_shutdown()
    Registrar.wait_for_shutdown()
    sys.exit(0)

def wait_for_tcp_connection():
    tcp_host = "0.0.0.0"
    tcp_port = 8080
    with socket(AF_INET, SOCK_STREAM) as tcp_server:
        while not Registrar.shutdown_requested():
            tcp_server.bind((tcp_host, tcp_port))
            tcp_server.listen()

            connection, _ = tcp_server.accept()
            TcpServerConnection(connection).start()

setdefaulttimeout(20)

Thread(target=wait_for_tcp_connection, daemon=True)

signal.signal(signal.SIGINT, shutdown_hook)
signal.pause()
