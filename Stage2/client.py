import argparse
import json
import os
import pygame
from pygame.locals import *
import random
import socket, select

from constants import *
import utils
from render import render_game_state

# Special code to center window
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Globals
CLIENT = None  # Set in main

# Pygame setup
pygame.init()
WINDOWS_TITLE = 'Demo'
SCREEN = pygame.display.set_mode(RESOLUTION, DOUBLEBUF)
pygame.display.set_caption(WINDOWS_TITLE)
PYGAME_CLOCK = pygame.time.Clock()
pygame.font.init()
script_path = os.path.dirname(os.path.realpath(__file__))
font_path = os.path.join(script_path, "assets/fonts/digital-7.ttf")
font_size = 24
FONT = pygame.font.Font(font_path, font_size)
DEBUG = False
DEBUG_FONT = pygame.font.Font(font_path, font_size)
GREEN = (0, 255, 0)
IS_FULLSCREEN = False

# Starry background
BACKGROUND = pygame.Surface(SCREEN.get_size()).convert()
BACKGROUND.fill((0, 0, 0))
for _ in range(100):
    pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
    BACKGROUND.set_at(pos, (255, 255, 255))

# Wrapper around socket to send and receive messages
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
            chunk = self.socket.recv(4096) # buffer of 4096
            if not chunk:  # Select returns but no data means connection is dead
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

def toggle_debug():
    global DEBUG
    DEBUG = not DEBUG

def toggle_fullscreen():
    global SCREEN, IS_FULLSCREEN
    IS_FULLSCREEN = not IS_FULLSCREEN
    screen = pygame.display.get_surface()
    tmp = screen.convert()
    caption = pygame.display.get_caption()
    bits = screen.get_bitsize()
    pygame.display.quit()
    pygame.display.init()

    if IS_FULLSCREEN:
        screen = pygame.display.set_mode(RESOLUTION, FULLSCREEN, bits)
    else:
        screen = pygame.display.set_mode(RESOLUTION, DOUBLEBUF, bits)
    screen.blit(tmp, (0, 0))
    pygame.display.set_caption(*caption)
    SCREEN = screen


if __name__ == '__main__':

    # Parse command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',
                        dest='host',
                        required=False,
                        help=("Host to connect to."))
    parser.add_argument('--port',
                        dest='port',
                        required=False,
                        type=int,
                        help=("Port to connect to."))
    args = parser.parse_args()

    args = parser.parse_args()
    print "Starting with parameters:"
    for arg, value in sorted(vars(args).items()):
        if value is not None:
            print "  %s: %s" % (arg, value)

    CLIENT = Client(args.host, args.port)
    CLIENT.connect()

    done = False
    while not done:
        # receive game_state from server
        game_state = CLIENT.receive()

        # only re-render when receive update
        if game_state:
            SCREEN.blit(BACKGROUND, (0, 0))  # clear screen

            render_game_state(SCREEN, game_state)
            if DEBUG:
                msg = "FPS: %.02f" % PYGAME_CLOCK.get_fps()
                SCREEN.blit(DEBUG_FONT.render(msg, 1, GREEN), (WIDTH - 350, 0))

            pygame.display.flip() # Copy offscreen buffer to video memory

        # get key presses and send to server
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE] or keys[K_q]:
            done = True
        if keys[K_LEFT]:
            CLIENT.send(TURN_LEFT)
        if keys[K_RIGHT]:
            CLIENT.send(TURN_RIGHT)
        if keys[K_UP]:
            CLIENT.send(THRUST)
        if keys[K_DOWN]:
            CLIENT.send(BACK_THRUST)
        if keys[K_SPACE]:
            CLIENT.send(SHOOT)
        if keys[K_f]:
            toggle_fullscreen()
        if keys[K_d]:
            toggle_debug()

        # Check if clicked exit box
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        PYGAME_CLOCK.tick(60)
