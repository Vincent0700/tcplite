# coding=utf-8

import tcplite


def handler(packet: tcplite.Packet, sock_from):
    data = packet.data
    print(data)


if __name__ == '__main__':
    client = tcplite.TCPClient(
        host='localhost',
        port=10086,
        handler=handler
    ).start()
