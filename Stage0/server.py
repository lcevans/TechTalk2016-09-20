# Simple Chat Server
# Modified from http://www.binarytides.com/code-chat-application-server-client-sockets-python/
# Provides skeleton for the later stages.

import socket, select
import argparse

# List to keep track of socket descriptors
SOCKET_LIST = []

# Broadcast message from from_fd to all other connected clients
def broadcast(message, from_fd):
    for socket in SOCKET_LIST:
        if socket != server_socket and socket.fileno() != from_fd:
            try:
                socket.send(message)
            except:
                # Broken connection.
                remove_client(sock.fileno())

def remove_client(id):
    print "Client %s going offline" % fd
    for sock in SOCKET_LIST:
        if sock.fileno() == id:
            sock.close()
            SOCKET_LIST.remove(sock)


if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('--port',
                        dest='port',
                        required=True,
                        help=("Port to serve on."))
    parser.add_argument('--max_clients',
                        dest='max_clients',
                        required=False,
                        type=int,
                        default=10,
                        help=("Max clients."))
    args = parser.parse_args()
    print "Starting with parameters:"
    for arg, value in sorted(vars(args).items()):
        if value is not None:
            print "  %s: %s" % (arg, value)


    # Add server socket to the list of connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", int(args.port)))
    server_socket.listen(args.max_clients)
    SOCKET_LIST.append(server_socket)
    print "Server started on port " + args.port

    while True:
	# Get the list sockets which are ready to be read through select
        read_sockets,_,_ = select.select(SOCKET_LIST,[],[])

        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                if len(SOCKET_LIST) < args.max_clients + 1:
                    sockfd, addr = server_socket.accept()
                    SOCKET_LIST.append(sockfd)
                    print "Client (%s, %s) connected" % addr
                else:
                    sockfd, addr = server_socket.accept()
                    sockfd.send('Too many connections \n')
                    sockfd.close()

            #Incoming message from a client
            else:
                try:
                    message = sock.recv(4096) # buffer of 4096
                    broadcast(message, sock.fileno())

                except Exception as e:
                    # Client disconnected or is messing with us
                    remove_client(sock.fileno())


    server_socket.close()
