# Eyegrade: grading multiple choice questions with a webcam
# Copyright (C) 2010-2015 Jesus Arias Fisteus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#

from __future__ import division

import math

import cv2
import numpy as np

from . import geometry as g
from . import utils


# Main image processing functions on numpy images
#
def width(image):
    """Returns the width of the numpy image in pixels."""
    return image.shape[1]

def height(image):
    """Returns the height of the numpy image in pixels."""
    return image.shape[0]

def new_image(width, height, num_channels):
    if num_channels == 1:
        image = np.zeros((height, width), np.uint8)
    elif num_channels == 3:
        image = np.zeros((height, width, 3), np.uint8)
    else:
        raise ValueError('Wrong number of channels in _new_image()')
    return image

def zero_image(image):
    image[:, :] = 0

def gray_to_rgb(image):
    return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

def rgb_to_gray(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


# Image reading and writing
#
def load_image_grayscale(filename):
    return cv2.imread(filename, flags=cv2.IMREAD_GRAYSCALE)

def load_image(filename):
    str_filename = utils.unicode_path_to_str(filename)
    return cv2.imread(str_filename)


# Drawing functions
#
def draw_line(image, line, color=(0, 0, 255, 0)):
    theta = line[1]
    points = set()
    if math.sin(theta) != 0.0:
        points.add(g.line_point(line, x=0))
        points.add(g.line_point(line, x=g.width(image) - 1))
    if math.cos(theta) != 0.0:
        points.add(g.line_point(line, y=0))
        points.add(g.line_point(line, y=g.height(image) - 1))
    p_draw = [p for p in points if p[0] >= 0 and p[1] >= 0
              and p[0] < g.width(image) and p[1] < g.height(image)]
    if len(p_draw) == 2:
        cv2.line(image, p_draw[0], p_draw[1], color, thickness=1)

def draw_point(image, point, color=(255, 0, 0, 0), radius=2):
    x, y = point
    if x >= 0 and x < g.width(image) and y >= 0 and y < g.height(image):
        cv2.circle(image, point, radius, color, thickness=-1)
    else:
        print "draw_point: bad point (%d, %d)"%(x, y)

def draw_text(image, text, color=(255, 0, 0), position=(10, 30)):
    cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1.0, color,
                thickness=3)
