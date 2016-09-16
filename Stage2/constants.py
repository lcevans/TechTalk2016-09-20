import colorsys

RESOLUTION = WIDTH, HEIGHT = 800, 600

SHIP_STATS = {
    'turn_speed' : 0.25,
    'thrust' : 15,
    'bullet_speed' : 200,
    'num_bullets' : 7,
    'max_speed' : 800,
}


# Event types
TURN_LEFT = 'TURN_LEFT'
TURN_RIGHT = 'TURN_RIGHT'
THRUST = 'THRUST'
BACK_THRUST = 'BACK_THRUST'
SHOOT = 'SHOOT'


# Color constants
NUM_COLORS = 10
# c.f. http://gamedev.stackexchange.com/questions/46463/how-can-i-find-an-optimum-set-of-colors-for-10-players
shot_colors_abs = [colorsys.hsv_to_rgb((i * 0.618033988749895 % 1.0), 0.5, 1.0)
                   for i in range(NUM_COLORS)]
shot_colors = [(255 * R, 255 * G, 255 * B) for R,G,B in shot_colors_abs]
# darker version of shot colors
ship_colors = [(int(R * 0.8),
                int(G * 0.8),
                int(B * 0.8))
               for R,G,B in shot_colors]
