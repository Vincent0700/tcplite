from tcplite import TCPServer

if __name__ == '__main__':
    server = TCPServer(port=10086)
    server.start()
