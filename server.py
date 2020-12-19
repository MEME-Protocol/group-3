#! /usr/bin/python3.9
import signal
import sys
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, setdefaulttimeout, socket
from threading import Thread

from model.tcp_server_connection import TcpServerConnection
from util.common import create_logger
from util.registrar import Registrar


def shutdown_hook(sig, frame):
    print("Shutdown requested")
    Registrar.request_shutdown()
    Registrar.wait_for_shutdown()
    sys.exit(0)


def wait_for_tcp_connection():
    log = create_logger("tcp_connection_thread")
    tcp_host = "0.0.0.0"
    tcp_port = 2000
    with socket(AF_INET, SOCK_STREAM) as tcp_server:
        tcp_server.bind((tcp_host, tcp_port))
        tcp_server.listen()
        log.info(f"Started tcp server at {tcp_host}:{tcp_port}")
        while not Registrar.shutdown_requested():
            connection, _ = tcp_server.accept()
            log.info("Server accepted connection")
            TcpServerConnection(connection).start()
    log.info("Stopped listening to tcp-connections")


setdefaulttimeout(20)

Thread(target=lambda: wait_for_tcp_connection(), daemon=True).start()

signal.signal(signal.SIGINT, shutdown_hook)
signal.pause()
