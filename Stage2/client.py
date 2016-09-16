import argparse
import json
import os
import pygame
from pygame.locals import *
import random

from constants import *
from network import Client
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

# Misc
SHIP_SIZE = 15

# Starry background
BACKGROUND = pygame.Surface(SCREEN.get_size()).convert()
BACKGROUND.fill((0, 0, 0))
for _ in range(100):
    pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
    BACKGROUND.set_at(pos, (255, 255, 255))


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
