# coding=utf-8

from tcplite import TCPClient
from tcplite.packet import Packet


def handler(packet: Packet, sock_from):
        data = packet.data
        print(data)


if __name__ == '__main__':
    client = TCPClient(
        host='localhost',
        port=10086,
        handler=handler
    ).start()
