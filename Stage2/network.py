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
        self.id = 0
        self.is_connected = False

    def connect(self):
        self.socket.connect((self.host, self.port))
        self.is_connected = True

    def send(self, message):
        msg = {"id": self.id, "type": message}
        msg = json.dumps(msg)
        self.socket.send(msg + '\n')

    def get_id(self):
        while True:
            read_sockets, _, _ = select.select([self.socket], [], [], 0)  # Non-blocking
            if read_sockets:
                # Grab the entire message
                chunk = self.socket.recv(RECV_BUFFER)
                self.buf += chunk
                # Find the first valid message
                end = self.buf.find("\n")
                msg = self.buf[:end]
                # Clean up buffer
                self.buf = self.buf[end + 1:]
                self.id = json.loads(msg)['id']
                return

    def set_nickname(self, nickname):
        msg = {"id": self.id, "type": NICKNAME, "nickname": nickname}
        msg = json.dumps(msg) + "\n"
        self.socket.send(msg)

    def receive(self):
        if not self.is_connected:
            print 'Server disconnected'
            sys.exit(0)
        read_sockets, _, _ = select.select([self.socket], [], [], 0)  # Non-blocking
        if read_sockets:
            # Grab the entire message
            chunk = self.socket.recv(RECV_BUFFER)
            if not chunk:  # Select returns but no data ==> connection to server is dead
                self.is_connected = False

            self.buf += chunk
            # Find the lastes valid message
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


if __name__ == '__main__':
    client = Client('127.0.0.1', 9999)
    client.connect()
    client.send({"id" : client.socket.fileno(), "type" : "KEY_LEFT"})
    msg = client.receive()
    print msg
