#! /usr/bin/python3.9
import signal
import sys
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, setdefaulttimeout, socket, timeout
from threading import Thread

from model.server.tcp_listener import TcpListener
from model.server.tcp_outgoing import TcpOutgoing
from util.common import create_logger


def shutdown_hook(sig, frame):
    sys.exit(0)


def wait_for_tcp_connection():
    tcp_outgoing = TcpOutgoing()
    tcp_outgoing.start()
    log = create_logger("tcp_connection_thread")
    tcp_host = "0.0.0.0"
    tcp_port = 2000
    with socket(AF_INET, SOCK_STREAM) as tcp_server:
        tcp_server.bind((tcp_host, tcp_port))
        tcp_server.listen()
        log.info(f"Started tcp server at {tcp_host}:{tcp_port}")
        while True:
            try:
                connection, _ = tcp_server.accept()
            except timeout:
                log.debug("Timeout received")
                continue

            log.info("Server accepted connection")
            TcpListener(connection, tcp_outgoing).start()
    log.info("Stopped listening to tcp-connections")


Thread(target=lambda: wait_for_tcp_connection(), daemon=True).start()

signal.signal(signal.SIGINT, shutdown_hook)
signal.pause()
