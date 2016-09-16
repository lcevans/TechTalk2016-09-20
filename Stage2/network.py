import sys
import socket, select
import json

RECV_BUFFER = 4096

class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buf = ""

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send(self, message):
        msg = {"type": message}
        msg = json.dumps(msg)
        self.socket.send(msg + '\n')

    def receive(self):
        read_sockets, _, _ = select.select([self.socket], [], [], 0)  # Non-blocking
        if read_sockets:
            # Grab the entire message
            chunk = self.socket.recv(RECV_BUFFER)
            if not chunk:  # Select returns but no data ==> connection to server is dead
                print "Lost connection to server"
                sys.exit(1)

            self.buf += chunk
            # Find the last valid message
            end = self.buf.rfind("\n")
            if end < 0:
                return
            start = self.buf.rfind("\n", 0, end - 1)
            if start < 0:
                start = 0
            msg = self.buf[start:end]
            # Clean up buffer
            self.buf = self.buf[end + 1:]
            return json.loads(msg)
