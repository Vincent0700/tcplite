# coding=utf-8
__author__ = 'wang.yuanqiu007@gmail.com'

import pickle
import json
import attr
import socket
import threading
from attr.validators import instance_of, optional
from enum import Enum

# The bytes at the end of the packet
EOF = b'\xFF\xFF\x00\x00'


class PacketParseError(Exception):
    def __init__(self, error):
        super().__init__(self, error)

    def __str__(self):
        return f'Packet parse error: {self.error}'


class EventType(Enum):
    """
    Packet route type

    Attributes:
        DIRECT_MSG: Indicate the packet is send to a direct socket.
        BROADCAST: Send to all the sockets except itself.
    """
    DIRECT_MSG = b'\x01'
    BROADCAST = b'\x02'

    @staticmethod
    def from_int(val=attr.ib(type=int, validator=instance_of(int))):
        if val == int(EventType.DIRECT_MSG.value.hex()):
            return EventType.DIRECT_MSG
        elif val == int(EventType.BROADCAST.value.hex()):
            return EventType.BROADCAST
        raise PacketParseError('Event type is not legal.')


class DataType(Enum):
    """
    Packet data type


    """
    RAW = b'\x01'  # raw data, no need to decode
    PICKLED = b'\x02'  # bytes -> python object
    STRING = b'\x03'  # bytes -> str
    JSON = b'\x04'  # bytes -> str -> dict

    @staticmethod
    def from_int(val):
        if val == int(DataType.RAW.value.hex()):
            return DataType.RAW
        elif val == int(DataType.PICKLED.value.hex()):
            return DataType.PICKLED
        elif val == int(DataType.STRING.value.hex()):
            return DataType.STRING
        elif val == int(DataType.JSON.value.hex()):
            return DataType.JSON
        raise PacketParseError(f'Unexpected datatype {str(val)}')


@attr.s
class Packet:
    event_type = attr.ib(type=EventType, validator=instance_of(EventType))  # required
    data_type = attr.ib(type=EventType, validator=instance_of(DataType))  # required
    data = attr.ib(default=None)

    class PacketParseError(Exception):
        def __init__(self, error):
            super().__init__(self, error)

        def __str__(self):
            return f'Packet parse error: {self.error}'

    def encode(self) -> attr.ib(type=bytes, validator=instance_of(bytes)):
        if self.data_type == DataType.RAW:
            raw = self.data
        elif self.data_type == DataType.PICKLED:
            raw = pickle.dumps(self.data)
        elif self.data_type == DataType.STRING:
            raw = self.data.encode('utf-8')
        elif self.data_type == DataType.JSON:
            raw = json.dumps(self.data).encode('utf-8')
        else:
            raw = b''
        return self.event_type.value + self.data_type.value + raw

    @staticmethod
    def decode(
        raw=attr.ib(type=bytes, validator=instance_of(bytes))
    ):
        if len(raw) < 2:
            raise PacketParseError(f'The packet is illegal.')
        event_type = EventType.from_int(raw[0])
        data_type = DataType.from_int(raw[1])
        raw_data = raw[2:]
        if data_type == DataType.RAW:
            data = raw_data
        elif data_type == DataType.PICKLED:
            data = pickle.loads(raw_data)
        elif data_type == DataType.STRING:
            data = raw_data.decode('utf-8')
        elif data_type == DataType.JSON:
            data = json.loads(raw_data.decode('utf-8'))
        else:
            raise PacketParseError(f'Cannot decode datatype {data_type.value}.')
        return Packet(
            event_type=event_type,
            data_type=data_type,
            data=data
        )


@attr.s(init=True)
class PacketReceiver:
    """
    The class continuously read buffer from socket.

    Attributes:
        sock: The socket we receive buffer from. Required.
        handler: The packet message handler. Default to None.
        chunk_size: The length of bytes we read at one time. Deafult to 1024.
        eof: The bytes at the end of packet buffer. Default to packet default eof.
        thread: The thread of reading handler. Default to None.
        is_alive: Bool indicates whether reading thread is alive. Default to True.
    """
    sock = attr.ib(type=socket.socket, validator=instance_of(socket.socket))
    handler = attr.ib(default=None)
    chunk_size = attr.ib(type=int, validator=instance_of(int), default=1024)
    eof = attr.ib(type=bytes, validator=instance_of(bytes), default=EOF)
    is_alive = attr.ib(type=bool, validator=instance_of(bool), default=True)
    thread = attr.ib(type=threading.Thread, default=None,
                     validator=optional([instance_of(threading.Thread), instance_of(None)]))

    def start_listen(self):
        self.is_alive = True
        self.thread = threading.Thread(target=self.reading)
        self.thread.start()

    def close(self):
        self.is_alive = False

    def reading(self):
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
                pass
