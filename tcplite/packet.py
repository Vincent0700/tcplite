# coding=utf-8
__author__ = 'wang.yuanqiu007@gmail.com'

import pickle
import json
import attr
from attr.validators import instance_of
from enum import Enum
from .error import PacketParseError

EOF = b'\xFF\xFF\x00\x00'


class EventType(Enum):
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
    RAW = b'\x01'  # raw data, no need to decode
    PICKLED = b'\x02'  # bytes -> object
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
        raise PacketParseError('Data type is not legal.')


@attr.s
class Packet:
    event_type = attr.ib(type=EventType, validator=instance_of(EventType))  # required
    data_type = attr.ib(type=EventType, validator=instance_of(DataType))  # required
    data = attr.ib(default=None)

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
            raise PacketParseError(f'Packet given is not incomplete.')
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
            raise PacketParseError('Do not know how to decode.')
        return Packet(
            event_type=event_type,
            data_type=data_type,
            data=data
        )
