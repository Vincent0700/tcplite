import tcplite

if __name__ == '__main__':
    server = tcplite.TCPServer(port=10086)
    server.start()
