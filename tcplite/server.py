# coding=utf-8
__author__ = 'wang.yuanqiu007@gmail.com'

import socket
import attr
from attr.validators import instance_of
from .receiver import SockReceiver
from .packet import EOF, Packet, EventType


@attr.s(init=True)
class ClientInfo(object):
    """
    Client information dataclass

    Attributes:
        socket: client socket
        addr: ip address like ('0.0.0.0', 8080)
        is_alive: end the socket loop if the value is false
    """

    socket = attr.ib(type=socket.socket, validator=instance_of(socket.socket))  # required
    addr = attr.ib(type=tuple, validator=instance_of(tuple))  # required
    is_alive = attr.ib(type=bool, validator=instance_of(bool), default=True)


@attr.s(init=True)
class TCPServer(object):
    """
    A basic server based on transport control protocol

    Attributes:
        host: server host
        port: server port
        backlog: the length of accept queue
        chunk_size: amount of data to read at one time
        timeout: connection timeout
        __socket: server socket
        __reader: socket reader, it will start a thread and continually read buffer from socket
        __clients: client information list
    """

    port = attr.ib(type=int, validator=instance_of(int))  # required
    host = attr.ib(type=str, validator=instance_of(str), default='0.0.0.0')
    backlog = attr.ib(type=int, validator=instance_of(int), default=5)
    chunk_size = attr.ib(type=int, validator=instance_of(int), default=1024)
    timeout = attr.ib(type=int, validator=instance_of(int), default=1 * 60 * 60)

    __socket = attr.ib(type=socket.socket, default=None)
    __reader = attr.ib(type=SockReceiver, default=None)
    __clients = attr.ib(type=dict, validator=instance_of(dict), default={})

    def __del__(self):
        """
        destructor
        """

        if self.__socket:
            self.__socket.close()
            print(f'[Info] Server is closed.')

    def start(self):
        """
        start server
        """

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((self.host, self.port))
        self.__socket.listen(self.backlog)
        print(f'[Info] Server is running at {self.host}:{self.port}')

        while True:
            try:
                # wait for connection
                client_socket, addr = self.__socket.accept()

                # add client info
                str_addr = addr[0] + str(addr[1])
                client_info = ClientInfo(socket=client_socket, addr=addr, is_alive=True)
                self.__clients[str_addr] = client_info

                # after connect
                self.on_connect(client_info)

            except KeyboardInterrupt:
                break

    def on_connect(
        self,
        client_info: ClientInfo
    ):
        """
        client socket connection handler

        :param {ClientInfo} client_info: client socket information
        """

        client_socket = client_info.socket
        client_addr = client_info.addr

        self.__reader = SockReceiver(
            sock=client_socket,
            handler=self.packet_handler,
            chunk_size=self.chunk_size,
            eof=EOF)
        self.__reader.start_listen()

    def packet_handler(self, buffer, sock_from: socket.socket):
        packet = Packet.decode(buffer)
        print(packet)
        if packet.event_type == EventType.BROADCAST:
            disconnects = []

            for address in self.__clients:
                client = self.__clients[address]
                if client.socket is not sock_from:
                    try:
                        client.socket.sendall(buffer + EOF)
                    except ConnectionError as e:
                        print(f'[Info] Dicsonnect from {address}')
                        # collect disconnect clients
                        disconnects.append(address)

            # drop disconnect clients
            for address in disconnects:
                self.__clients.pop(address)
