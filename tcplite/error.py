# coding=utf-8
__author__ = 'wang.yuanqiu007@gmail.com'


class PacketParseError(Exception):
    def __init__(self, error):
        super().__init__(self, error)

    def __str__(self):
        return f'Packet parse error: {self.error}'
