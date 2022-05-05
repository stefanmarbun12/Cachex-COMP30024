"""
COMP30024 Artificial Intelligence, Semester 1, 2022
Testing tool for Project Part B
Extension on https://github.com/ANDREYDEN/Hex-Game for Cachex, by Stefan Marbun
Please use this code for testing purposes only, do not copy anything directly to use in your project submission
"""

import pygame as pg
from itertools import islice, product
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


def print_coordinate(r, q, **kwargs):
    """
    Output an axial coordinate (r, q) according to the format instructions.

    Any keyword arguments are passed through to the print function.
    """
    print(f"({r},{q})", **kwargs)


def print_board(n, board_dict, message="", ansi=False, **kwargs):
    """
    For help with visualisation and debugging: output a board diagram with
    any information you like (tokens, heuristic values, distances, etc.).

    Arguments:

    n -- The size of the board
    board_dict -- A dictionary with (r, q) tuples as keys (following axial
        coordinate system from specification) and printable objects (e.g.
        strings, numbers) as values.
        This function will arrange these printable values on a hex grid
        and output the result.
        Note: At most the first 5 characters will be printed from the string
        representation of each value.
    message -- A printable object (e.g. string, number) that will be placed
        above the board in the visualisation. Default is "" (no message).
    ansi -- True if you want to use ANSI control codes to enrich the output.
        Compatible with terminals supporting ANSI control codes. Default
        False.

    Any other keyword arguments are passed through to the print function.

    Example:

        >>> board_dict = {
        ...     (0, 4): "hello",
        ...     (1, 1): "r",
        ...     (1, 2): "b",
        ...     (3, 2): "$",
        ...     (2, 3): "***",
        ... }
        >>> print_board(5, board_dict, "message goes here", ansi=False)
        # message goes here
        #              .-'-._.-'-._.-'-._.-'-._.-'-.
        #             |     |     |     |     |     |
        #           .-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #          |     |     |  $  |     |     |
        #        .-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #       |     |     |     | *** |     |
        #     .-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #    |     |  r  |  b  |     |     |
        #  .-'-._.-'-._.-'-._.-'-._.-'-._.-'
        # |     |     |     |     |hello| 
        # '-._.-'-._.-'-._.-'-._.-'-._.-'

    """

    stitch_pattern = ".-'-._"
    edge_col_len = 3
    v_divider = "|"
    h_spacing = len(stitch_pattern)
    output = message + "\n"

    # Helper function to only selectively apply ansi formatting if enabled
    apply_ansi_s = apply_ansi if ansi else lambda str, **_: str

    # Generator to repeat pattern string (char by char) infinitely
    def repeat(pattern):
        while True:
            for c in pattern:
                yield c

    # Generate stitching pattern given some offset and length
    def stitching(offset, length):
        return "".join(islice(repeat(stitch_pattern), offset, length))

    # Loop through each row i from top (print ordering)
    # Note that n - i - 1 is equivalent to r in axial coordinates
    for i in range(n):
        x_padding = (n - i - 1) * int(h_spacing / 2)
        stitch_length = (n * h_spacing) - 1 + \
                        (int(h_spacing / 2) + 1 if i > 0 else 0)
        mid_stitching = stitching(0, stitch_length)

        # Handle coloured borders for ansi outputs
        # Fairly ugly code, but there is no "simple" solution
        if i == 0:
            mid_stitching = apply_ansi_s(mid_stitching, color="r")
        else:
            mid_stitching = \
                apply_ansi_s(mid_stitching[:edge_col_len], color="b") + \
                mid_stitching[edge_col_len:-edge_col_len] + \
                apply_ansi_s(mid_stitching[-edge_col_len:], color="b")

        output += " " * (x_padding + 1) + mid_stitching + "\n"
        output += " " * x_padding + apply_ansi_s(v_divider, color="b")

        # Loop through each column j from left to right
        # Note that j is equivalent to q in axial coordinates
        for j in range(n):
            coord = (n - i - 1, j)
            value = str(board_dict.get(coord, ""))
            contents = value.center(h_spacing - 1)
            if ansi:
                contents = apply_ansi_s(contents, color=value)
            output += contents + (v_divider if j < n - 1 else "")
        output += apply_ansi_s(v_divider, color="b")
        output += "\n"

    # Final/lower stitching (note use of offset here)
    stitch_length = (n * h_spacing) + int(h_spacing / 2)
    lower_stitching = stitching(int(h_spacing / 2) - 1, stitch_length)
    output += apply_ansi_s(lower_stitching, color="r") + "\n"

    # Print to terminal (with optional args forwarded)
    print(output, **kwargs)
