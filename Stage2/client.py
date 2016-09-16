import argparse
import json
import os
import pygame
import pygame.gfxdraw
from pygame.locals import *
import random

from constants import *
from network import Client
import utils

# Special code to center window
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Globals
CLIENT = None  # Set in main

# Pygame setup
pygame.init()
WINDOWS_TITLE = 'PewPewPew Dev Demo'
SCREEN = pygame.display.set_mode(RESOLUTION, DOUBLEBUF)
pygame.display.set_caption(WINDOWS_TITLE)
CLOCK = pygame.time.Clock()
pygame.font.init()
script_path = os.path.dirname(os.path.realpath(__file__))
font_path = os.path.join(script_path, "assets/fonts/digital-7.ttf")
font_size = 24
FONT = pygame.font.Font(font_path, font_size)
DEBUG = False
DEBUG_FONT = pygame.font.Font(font_path, font_size)
END_FONT = pygame.font.Font(font_path, 64)
GREEN = (0, 255, 0)
NICKNAME_FONT = pygame.font.Font(font_path, 14)
# pygame.mixer.init()
IS_FULLSCREEN = False

BAD_SCORE = False

# Misc
SHIP_COLOR = (255, 255, 255)
EMEMY_SHIP_COLOR = (255, 0, 0)
SHIP_SIZE = 15
BULLET_COLOR = (0, 255, 127)
ENEMY_BULLET_COLOR = (255, 0, 0)
BACKGROUND = pygame.Surface(SCREEN.get_size()).convert()
BACKGROUND.fill((0, 0, 0))
for _ in range(100):
    pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
    BACKGROUND.set_at(pos, (255, 255, 255))


def shoot():
    CLIENT.send(SHOOT)

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


def render_game_state(game_state):
    SCREEN.blit(BACKGROUND, (0, 0))  # clear screen

    for ship in game_state['ships']:
        render_ship(ship)
        for shot in ship['shots']:
            render_shot(ship['id'], shot)

    if DEBUG:
        fps = CLOCK.get_fps()
        msg = "FPS: %.02f" % fps
        put_text(DEBUG_FONT, (WIDTH - 350, 0), GREEN, msg)

    # All drawing and operations on screen happends in a buffer
    # this dump all the drawings from the buffer to the actual
    # video memory
    pygame.display.flip()


def render_ship(ship):
    center_x, center_y = ship['x'], HEIGHT - ship['y']  # Translate between math coord and pygame coord

    # Other points defined form center of ship. (Will rotate later)
    tip_x, tip_y = center_x, center_y - SHIP_SIZE
    left_wing_x, left_wing_y = center_x - SHIP_SIZE, center_y + SHIP_SIZE
    right_wing_x, right_wing_y = center_x + SHIP_SIZE, center_y + SHIP_SIZE

    polygon = [(left_wing_x, left_wing_y),
               (tip_x, tip_y),
               (right_wing_x, right_wing_y),
               (center_x, center_y)]
    bottom = max(polygon, key=lambda pos: pos[1])
    left = min(polygon, key=lambda pos: pos[0])
    rotated_polygon = utils.rotate_polygon((center_x, center_y), polygon, float(ship['ang']))
    color = ship_colors[ship['id'] % len(ship_colors)]
    pygame.gfxdraw.filled_polygon(SCREEN, rotated_polygon, color)



def render_shot(id, shot):
    pos = (int(shot['x']), HEIGHT - int(shot['y']))  # Translate between math coord and pygame coord
    color = shot_colors[id % len(shot_colors)]
    pygame.draw.circle(SCREEN, color, pos, 2)


def put_text(font, pos, color, text):
    if not text:
        return
    SCREEN.blit(font.render(text, 1, color), pos)


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
    CLIENT.get_id()

    done = False
    while not done:
        # receive and render from server
        game_state = CLIENT.receive()
        if game_state:
            render_game_state(game_state)

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
            shoot()
        if keys[K_f]:
            toggle_fullscreen()
        if keys[K_d]:
            toggle_debug()

        # Check for clicking exit box?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        CLOCK.tick(60)
