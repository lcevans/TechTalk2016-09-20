import math
import pygame.gfxdraw
from constants import *

def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    theta = -1 * (angle - (math.pi / 2))

    a = math.cos(theta)
    b = math.sin(theta)

    qx = ox + a * (px - ox) - b * (py - oy)
    qy = oy + b * (px - ox) + a * (py - oy)
    return qx, qy

def render_game_state(SCREEN, game_state):
    for ship in game_state['ships']:
        render_ship(SCREEN, ship)
        for shot in ship['shots']:
            render_shot(SCREEN, ship['id'], shot)

def render_ship(SCREEN, ship):
    SHIP_SIZE = 15

    # Translate between math coord and pygame coord
    center_x, center_y = ship['x'], HEIGHT - ship['y']

    # Other points defined relative to center of ship. (Will rotate later)
    tip_x, tip_y = center_x, center_y - SHIP_SIZE
    left_wing_x, left_wing_y = center_x - SHIP_SIZE, center_y + SHIP_SIZE
    right_wing_x, right_wing_y = center_x + SHIP_SIZE, center_y + SHIP_SIZE

    polygon = [(left_wing_x, left_wing_y),
               (tip_x, tip_y),
               (right_wing_x, right_wing_y),
               (center_x, center_y)]
    rotated_polygon = [rotate((center_x, center_y), point, float(ship['ang']))
                       for point in polygon]

    color = ship_colors[ship['id'] % len(ship_colors)]
    pygame.gfxdraw.filled_polygon(SCREEN, rotated_polygon, color)

def render_shot(SCREEN, id, shot):
    pos = (int(shot['x']), HEIGHT - int(shot['y']))  # Translate between math coord and pygame coord
    color = shot_colors[id % len(shot_colors)]
    pygame.draw.circle(SCREEN, color, pos, 2)
