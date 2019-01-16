# coding=utf-8

import time
import tcplite


def task(tcp_client):
    while True:
        msg = tcplite.Packet(
            event_type=tcplite.EventType.BROADCAST,
            data_type=tcplite.DataType.JSON,
            data=dict(
                name='Vincent',
                greetings='Hello my friend'
            )
        ).encode()
        tcp_client.send(msg)
        time.sleep(0.5)


if __name__ == '__main__':
    client = tcplite.TCPClient(
        host='localhost',
        port=10086,
        task=task
    ).start()
