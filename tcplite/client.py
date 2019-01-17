# coding=utf-8
__author__ = 'wang.yuanqiu007@gmail.com'

import socket
import time
from .packet import EOF, Packet, PacketReceiver


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
        try:
            self.sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_server.connect((self.host, self.port))
            self.reader = PacketReceiver(
                sock=self.sock_server,
                handler=self.on_receive,
                chunk_size=self.chunk_size,
                eof=EOF)
            self.reader.start_listen()
            self.on_start()
        except ConnectionError:
            print('Connect Error.')
            print('Wait for 3 seconds to reconnect.')
            time.sleep(1)
            print('Wait for 2 seconds to reconnect.')
            time.sleep(1)
            print('Wait for 1 seconds to reconnect.')
            time.sleep(1)
            self.start()

    def send(self, msg):
        try:
            self.sock_server.sendall(msg + EOF)
        except ConnectionError:
            print('Connect Error.')
            self.reader.close()
            print('Wait for 3 seconds to reconnect.')
            time.sleep(1)
            print('Wait for 2 seconds to reconnect.')
            time.sleep(1)
            print('Wait for 1 seconds to reconnect.')
            time.sleep(1)
            self.start()

    def on_start(self):
        if self.task:
            self.task(self)

    def on_receive(self, buffer, sock_from):
        if self.handler:
            packet = Packet.decode(buffer)
            self.handler(packet, sock_from)
