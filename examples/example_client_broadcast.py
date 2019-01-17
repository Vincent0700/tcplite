import time
from tcplite import TCPClient
from tcplite import EventType, DataType, Packet


def task(tcp_client):
    while True:
        try:
            msg = Packet(
                event_type=EventType.BROADCAST,
                data_type=DataType.JSON,
                data=dict(
                    name='Vincent',
                    greetings='Hello my friend'
                )
            ).encode()
            tcp_client.send(msg)
            time.sleep(0.5)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    client = TCPClient(
        host='localhost',
        port=10086,
        task=task
    ).start()
