# Server for PewPewPew

import socket, select
import json
import time
import math
import argparse
import random

import utils
from constants import *

# Prettify serialized JSON
class PrettyFloat(float):
    def __repr__(self):
        return '%.1f' % self

def pretty_floats(obj):
    if isinstance(obj, float):
        return PrettyFloat(obj)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_floats, obj)
    return obj

# List to keep track of socket descriptors
SOCKET_LIST = []

# Source of truth for game state
# Will be filled in by code below
game_state = {
    'ships': []
}

def reset_ship(ship):
    ship['x'] = random.random() * WIDTH
    ship['y'] = random.random() * HEIGHT
    ship['v_x'] = 0
    ship['v_y'] = 0
    ship['ang'] = random.random() * 2 * math.pi
    ship['shots'] = []

def add_new_ship(fd):
    # Add in random location
    ship = {
        'id': fd
    }
    reset_ship(ship)
    game_state['ships'].append(ship)

def remove_ship(fd):
    print "Client %s going offline" % fd
    for ship in game_state['ships']:
        if ship['id'] == fd:
            game_state['ships'].remove(ship)

    for sock in SOCKET_LIST:
        if sock.fileno() == fd:
            sock.close()
            SOCKET_LIST.remove(sock)

# Broadcast game state to all connected clients
def broadcast_game_state():
    for socket in SOCKET_LIST:
        if socket != server_socket:
            try :
                socket.send(json.dumps(pretty_floats(game_state)) + '\n')
            except :
                # Broken connection.
                remove_ship(sock.fileno())

def update_positions(time_delta):
    # update ship position
    for ship in game_state['ships']:
        ship['x'] += ship['v_x'] * time_delta
	ship['x'] %= WIDTH
        ship['y'] += ship['v_y'] * time_delta
	ship['y'] %= HEIGHT

        # update shot position
        for shot in ship['shots']:
            shot['x'] += shot['v_x'] * time_delta
	    shot['x'] %= WIDTH
            shot['y'] += shot['v_y'] * time_delta
	    shot['y'] %= HEIGHT

            # check for shot hits
            for other_ship in game_state['ships']:
                if other_ship != ship:
                    delta_x = math.fabs(shot['x'] - other_ship['x'])
                    delta_y = math.fabs(shot['y'] - other_ship['y'])
                    if delta_x < 15 and delta_y < 15:
                        reset_ship(other_ship)

def handle_client_event(fd, event):
    for ship in game_state['ships']:
        if ship['id'] == fd:
            if event['type'] == TURN_LEFT:
                ship['ang'] += SHIP_STATS['turn_speed']
                ship['ang'] %= 2 * math.pi
            if event['type'] == TURN_RIGHT:
                ship['ang'] -= SHIP_STATS['turn_speed']
                ship['ang'] %= 2 * math.pi
            if event['type'] == THRUST:
                ship['v_x'] += math.cos(ship['ang']) * SHIP_STATS['thrust']
                ship['v_y'] += math.sin(ship['ang']) * SHIP_STATS['thrust']
            if event['type'] == BACK_THRUST:
                ship['v_x'] -= math.cos(ship['ang']) * SHIP_STATS['thrust']
                ship['v_y'] -= math.sin(ship['ang']) * SHIP_STATS['thrust']
            if event['type'] == SHOOT:
                new_shot = {
                    'x' : ship['x'],
                    'y' : ship['y'],
                    'v_x' : math.cos(ship['ang']) * SHIP_STATS['bullet_speed'],
                    'v_y' : math.sin(ship['ang']) * SHIP_STATS['bullet_speed'],
                }
                ship['shots'].append(new_shot)
        # Remove extra bullets
        if len(ship['shots']) > SHIP_STATS['num_bullets']:
            ship['shots'].pop(0)
        # Cap speed
        speed = math.sqrt(ship['v_x'] ** 2 + ship['v_y'] ** 2)
        if speed > SHIP_STATS['max_speed']:
            v_ang = math.atan2(ship['v_y'], ship['v_x'])
            ship['v_x'] = SHIP_STATS['max_speed'] * math.cos(v_ang)
            ship['v_y'] = SHIP_STATS['max_speed'] * math.sin(v_ang)



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
    print "Game server started on port " + args.port

    while True:
	# Get the list sockets which are ready to be read through select
        read_sockets,_,_ = select.select(SOCKET_LIST,[],[],0)

        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                if len(SOCKET_LIST) < args.max_clients + 1:
                    sockfd, addr = server_socket.accept()
                    SOCKET_LIST.append(sockfd)
                    print "Client (%s, %s) connected" % addr
                    fd = sockfd.fileno()
                    if not any(ship for ship in game_state['ships'] if fd == ship['id']): # Handle multiship bug
                        add_new_ship(fd)
                else:
                    sockfd, addr = server_socket.accept()
                    sockfd.send('Too many players \n')
                    sockfd.close()

            #Incoming message from a client
            else:
                try:
                    data = sock.recv(4096) # buffer of 4096
                    event_strings = data.strip().split('\n')
                    for event_str in event_strings:
                        event = json.loads(event_str)
                        handle_client_event(sock.fileno(), event)

                except Exception as e:
                    # Client disconnected or is messing with us
                    remove_ship(sock.fileno())
                    continue

        UPDATE_INTERVAL = 0.02
        time.sleep(UPDATE_INTERVAL)
        update_positions(UPDATE_INTERVAL)

        broadcast_game_state()

    server_socket.close()
