import math


def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    theta = -1 * (angle - (math.pi / 2))

    a = math.cos(theta)
    b = math.sin(theta)

    qx = ox + a * (px - ox) - b * (py - oy)
    qy = oy + b * (px - ox) + a * (py - oy)
    return qx, qy


def rotate_polygon(ref, polygon, angle):
    return [rotate(ref, point, angle) for point in polygon]


def get_speeds(speed, angle):
    theta = math.radians(angle)
    a, b = math.cos(theta), math.sin(theta)
    dx = speed * b
    dy = speed * a
    return dx, dy
