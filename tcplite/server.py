# coding=utf-8
__author__ = 'wang.yuanqiu007@gmail.com'

import socket
import attr
from attr.validators import instance_of
from .packet import EOF, Packet, EventType, PacketReceiver


@attr.s(init=True)
class TCPServer(object):
    """
    A basic server based on transport control protocol

    Attributes:
        port: The port number for the server to listen on.
        host: The hostname or IP address for the server to listen on. Defaults to 0.0.0.0.
        backlog: The length of server socket accept queue. Defaults to 5.
        chunk_size: Amount of data to read at one time. Default to 1024.
        heartbeat: The time in seconds that server send heartbeat to client. Default to 10s.
        sock_server: The socket of server.
        is_alive: The boolean indicate whether server is running. It will end up accept loop when it turned to False.
        reader: The SocketReader for the server. it will start a thread and continually read buffer from socket.
        clients: Clients information dict.
    """
    port = attr.ib(type=int, validator=instance_of(int))  # required
    host = attr.ib(type=str, validator=instance_of(str), default='0.0.0.0')
    backlog = attr.ib(type=int, validator=instance_of(int), default=5)
    chunk_size = attr.ib(type=int, validator=instance_of(int), default=1024)
    heartbeat = attr.ib(type=int, validator=instance_of(int), default=10)
    sock_server = attr.ib(type=socket.socket, default=None)
    is_alive = attr.ib(type=bool, validator=instance_of(bool), default=True)
    reader = attr.ib(type=PacketReceiver, default=None)
    clients = attr.ib(type=dict, validator=instance_of(dict), default={})

    @attr.s(init=True)
    class ClientInfo(object):
        """
        Client information dataclass

        Attributes:
            socket: The socket for client
            addr: The tuple (ip, port) of the client
            is_alive: The boolean indicate whether client is running.
        """
        socket = attr.ib(type=socket.socket, validator=instance_of(socket.socket))  # required
        addr = attr.ib(type=tuple, validator=instance_of(tuple))  # required
        is_alive = attr.ib(type=bool, validator=instance_of(bool), default=True)

    def __del__(self):
        if self.sock_server:
            self.sock_server.close()
            print(f'[Info] Server is closed.')

    def start(self):
        self.sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # reducing the "address already in use" error.
        # SO_REUSEADDR option allows a process to bind to a port which remains in TIME_WAIT
        # (it still only allows a single process to be bound to that port)
        self.sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_server.bind((self.host, self.port))
        self.sock_server.listen(self.backlog)
        self.is_alive = True
        print(f'[Info] Server is running at {self.host}:{self.port}')

        while self.is_alive:
            try:
                # wait until someone connected
                client_socket, addr = self.sock_server.accept()

                # add client info
                str_addr = addr[0] + str(addr[1])
                client_info = TCPServer.ClientInfo(socket=client_socket, addr=addr, is_alive=True)
                self.clients[str_addr] = client_info

                # create a PacketReceiver and start listening at a new thread
                self.reader = PacketReceiver(
                    sock=client_socket,
                    handler=self.packet_handler,
                    chunk_size=self.chunk_size,
                    eof=EOF)
                self.reader.start_listen()

            except KeyboardInterrupt:
                self.is_alive = False
                break

    def stop(self):
        """
        Set is_alive = False. It will stop server listening loop.
        """
        self.is_alive = False

    def packet_handler(
        self,
        buffer=attr.ib(type=bytes, validator=instance_of(bytes)),
        sock_from=attr.ib(type=socket, validator=instance_of(socket.socket))
    ):
        """
        The packet handler callback function invoked by PacketReceiver.

        :param buffer: Receiving packet raw data.
        :param sock_from: The socket who send packet.
        """
        # decode received packet
        packet = Packet.decode(buffer)
        print(packet)

        # handler broadcast message and
        # send packet to all the clients except itself
        if packet.event_type == EventType.BROADCAST:

            # disconnected client list
            disconnects = []

            for address in self.clients:
                client = self.clients[address]
                if client.socket is not sock_from:
                    try:
                        client.socket.sendall(buffer + EOF)
                    except ConnectionError as e:
                        print(f'[Info] Dicsonnect from {address}')

                        # collect disconnect clients
                        disconnects.append(address)

            # drop disconnect clients
            for address in disconnects:
                self.clients.pop(address)
