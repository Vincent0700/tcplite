# coding=utf-8
__author__ = 'wang.yuanqiu007@gmail.com'

import socket
from .receiver import SockReceiver
from .packet import EOF, Packet


class TCPClient(object):
    def __init__(self, host, port, task=None, handler=None):
        self.host = host
        self.port = port
        self.task = task
        self.handler = handler
        self.sock_server = None
        self.thread_listen = None
        self.chunk_size = 10
        self.reader = None

    def start(self):
        self.sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_server.connect((self.host, self.port))
        reader = SockReceiver(
            sock=self.sock_server,
            handler=self.on_receive,
            chunk_size=self.chunk_size,
            eof=EOF)
        reader.start_listen()
        self.on_start()

    def send(self, msg):
        self.sock_server.sendall(msg + EOF)

    def on_start(self):
        if self.task:
            self.task(self)

    def on_receive(self, buffer, sock_from):
        if self.handler:
            packet = Packet.decode(buffer)
            self.handler(packet, sock_from)
