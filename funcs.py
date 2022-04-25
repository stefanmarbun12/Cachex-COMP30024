"""
COMP30024 Artificial Intelligence, Semester 1, 2022
Testing tool for Project Part B
Extension on https://github.com/ANDREYDEN/Hex-Game for Cachex, by Stefan Marbun
Please use this code for testing purposes only, do not copy anything directly to use in your project submission
"""

import pygame as pg
from math import sqrt, hypot, pi, sin, cos
from collections import deque


class Point:
    def __init__(self, *pos):
        if len(pos) == 1:
            self.x, self.y = pos[0]
            self.X, self.Y = list(map(int, pos[0]))
        else:
            self.x, self.y = pos
            self.X, self.Y = list(map(int, pos))

    def dist(self, other):
        return hypot(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __str__(self):
        return '[x:{x}, y:{y}]'.format(x=self.x, y=self.y)

    def __iter__(self):
        """For unpacking"""
        return (x for x in (self.x, self.y))


# constants
DARK_RED = (155, 0, 0)
RED = (255, 0, 0)
LIGHT_RED = (255, 80, 80)
BLUE = (0, 0, 255)
LIGHT_BLUE = (51, 153, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 128, 0)
EPS = 0.0000000001
FPS = 30
MAX_BOARD_SIZE = 15
MIN_BOARD_SIZE = 3

# setup()
TILE_IMG = 'tile.png'
BG_IMG = 'bg.jpg'
PAUSE_IMG = 'pause.png'
BACK_IMG = 'back.png'
UP_IMG = 'up-arrow.png'
DOWN_IMG = 'down-arrow.png'
RULES = 'rules.txt'
CLICK_SOUND = 'click.wav'
# size of the window
W = 600
H = 600
# default size of the grid
SIZE = 8
moves = [Point(1, 0), Point(1, -1), Point(0, 1), Point(0, -1), Point(-1, 1), Point(-1, 0)]
POSSIBLE_DIAMONDS = [[(2, -1), (0, 0), (1, -1), (1, 0)], [(0, 0), (-2, 1), (-1, 0), (-1, 1)],
                     [(1, -1), (-1, 0), (0, -1), (0, 0)], [(1, 0), (-1, 1), (0, 1), (0, 0)],
                     [(1, 0), (0, 0), (1, -1), (0, 1)], [(0, 0), (-1, 0), (0, -1), (-1, 1)],
                     [(1, -1), (0, -1), (1, -2), (0, 0)], [(0, 1), (-1, 1), (0, 0), (-1, 2)],
                     [(1, -1), (0, 0), (0, -1), (1, 0)], [(0, 0), (-1, 1), (-1, 0), (0, 1)],
                     [(0, -1), (-1, 0), (-1, -1), (0, 0)], [(1, 0), (0, 1), (0, 0), (1, 1)]]


def triangle_s(a, b, c):
    """Return the surface of a triangle"""
    dist_a = c.dist(b)
    dist_b = a.dist(c)
    dist_c = a.dist(b)
    p = (dist_a + dist_b + dist_c) / 2
    return sqrt(p * (p - dist_a) * (p - dist_b) * (p - dist_c))


def in_hex(pos, x, y, a):
    """Checks if a point is in a hexagon"""
    point = Point(pos)
    points = [(x + a, y), (x + a / 2, y + a * sqrt(3) / 2),
              (x - a / 2, y + a * sqrt(3) / 2), (x - a, y),
              (x - a / 2, y - a * sqrt(3) / 2), (x + a / 2, y - a * sqrt(3) / 2)]
    points = list(map(Point, points))
    point_sum = 0
    for i in range(-1, 5):
        point_sum += triangle_s(points[i], points[i + 1], point)
    s = a * a * 3 * sqrt(3) / 2
    return abs(s - point_sum) < EPS


def in_rect(pos, x, y, w, h):
    """Checks if a point is in a rectangle"""
    return x < pos.x < x + w and y < pos.y < y + h


def pointy_hex_corner(center, size, i):
    x, y = center
    angle_deg = 60 * i - 30
    angle_rad = pi / 180 * angle_deg
    return x + size * cos(angle_rad), y + size * sin(angle_rad)


def draw_hex(surface, col_in, col_out, pos, a, r, c, size):
    x, y = pos
    points = [pointy_hex_corner((x, y), a, 0),
              pointy_hex_corner((x, y), a, 1),
              pointy_hex_corner((x, y), a, 2),
              pointy_hex_corner((x, y), a, 3),
              pointy_hex_corner((x, y), a, 4),
              pointy_hex_corner((x, y), a, 5)]

    # draw numbers and colored borders
    if c == 0:
        pg.draw.polygon(surface, BLUE, points[3:], 12)
        text_out(surface, r, 15, WHITE, (x - a * 1.5, y))
    if c == size - 1:
        pg.draw.polygon(surface, BLUE, points[:3], 12)
    if r == size - 1:
        pg.draw.polygon(surface, RED, points[4:] + points[:1], 12)
    if r == 0:
        pg.draw.polygon(surface, RED, points[1:4], 12)
        text_out(surface, c, 15, WHITE, (x, y + a * 1.5))
    # draw hexagon
    pg.draw.polygon(surface, col_in, points)
    pg.draw.polygon(surface, col_out, points, 4)


def in_bounds(v, w, h):
    return 0 <= v.X < h and 0 <= v.Y < w


def dfs(start, grid, end, player):
    w = len(grid[0])
    h = len(grid)
    queue = deque()
    queue.append(start)
    used = [[False for _ in range(w)] for __ in range(h)]
    while len(queue):
        cur = queue[-1]
        if end(cur):
            return True
        used[cur.X][cur.Y] = True
        flag = False
        for m in moves:
            other = cur + m
            if (in_bounds(other, w, h) and not used[other.X][other.Y]) \
                    and grid[other.X][other.Y] == player:
                queue.append(other)
                flag = True
                break
        if not flag:
            queue.pop()
    return False


def text_rect(txt, size):
    font = pg.font.SysFont('Verdana', size)
    text = font.render(txt, False, BLACK)
    return text.get_rect()


def text_out(surface, data, size, col, pos):
    txt = str(data)
    font = pg.font.SysFont('Verdana', size)
    text = font.render(txt, False, col)
    rect = text.get_rect(center=pos)
    surface.blit(text, rect)


def text_out_multiline(surface, txt, size, col, pos):
    font = pg.font.SysFont('Verdana', size)
    for y, line in enumerate(txt.split('\n')):
        text = font.render(line, False, col)
        rect = text.get_rect(center=(pos[0], pos[1] + (y + 5) * size))
        surface.blit(text, rect)
