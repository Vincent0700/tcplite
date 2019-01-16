# coding=utf-8
__author__ = 'wang.yuanqiu007@gmail.com'

import threading
from .packet import EOF


class SockReceiver:
    def __init__(self, sock, handler=None, chunk_size=1024, eof=EOF):
        self.sock = sock
        self.handler = handler
        self.chunk_size = chunk_size
        self.eof = eof
        self.thread = None
        self.is_alive = True

    def start_listen(self):
        self.is_alive = True
        self.thread = threading.Thread(target=self.async_reader)
        self.thread.start()

    def close(self):
        self.is_alive = False

    def async_reader(self):
        buffer = b''
        while self.is_alive:
            try:
                data = self.sock.recv(self.chunk_size)
                buffer += data
                arr = buffer.split(self.eof)
                arr_len = len(arr)
                for i in range(arr_len - 1):
                    self.handler(arr[i], self.sock)
                buffer = arr[-1] if arr[-1] else b''
            except ConnectionError as e:
                print(e)
