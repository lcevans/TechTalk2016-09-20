## Functions to update game_state

import math
import random

from constants import *

def update_positions(game_state, time_delta):
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
                        reset_ship(game_state, other_ship)

def reset_ship(game_state, ship):
    ship['x'] = random.random() * WIDTH
    ship['y'] = random.random() * HEIGHT
    ship['v_x'] = 0
    ship['v_y'] = 0
    ship['ang'] = random.random() * 2 * math.pi
    ship['shots'] = []

def add_new_ship(game_state, fd):
    # Add in random location
    ship = {
        'id': fd
    }
    reset_ship(game_state, ship)
    game_state['ships'].append(ship)

def remove_ship(game_state, id):
    for ship in game_state['ships']:
        if ship['id'] == id:
            game_state['ships'].remove(ship)
