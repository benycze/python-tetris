#!/usr/bin/env python3

# File: block.py
# Description: This file contains the declaration of basic tetris block class.
# Author: Pavel Benáček <pavel.benacek@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import copy
import math
import pygame
import constants


class Block:
    """
    Class for handling of tetris block
    """

    def __init__(self, shape, x, y, screen, color, rotate_en):
        """
        Initialize the tetris block class

        Parameters:
            - shape - list of block data with relative [X, Y] coordinates
                      of building blocks.
            - x - X coordinate of first tetris shape block
            - y - Y coordinate of first tetris shape block
            - screen - screen to draw on
            - color - the color of each shape block in RGB notation
            - rotate_en - enable or disable the rotation
        """
        # The initial shape (convert all to Rect objects)
        self.shape = []
        for sh in shape:
            bx = sh[0] * constants.BWIDTH + x
            by = sh[1] * constants.BHEIGHT + y
            block = pygame.Rect(bx, by, constants.BWIDTH, constants.BHEIGHT)
            self.shape.append(block)
        # Setup the rotation attribute
        self.rotate_en = rotate_en
        # Setup the rest of variables
        self.x = x
        self.y = y
        # Movement in the X,Y coordinates
        self.diffx = 0
        self.diffy = 0
        # Screen to draw on
        self.screen = screen
        self.color = color
        # Rotation angle
        self.diff_rotation = 0
        # Backup state
        self.shape_copy = []
        self.x_copy = x
        self.y_copy = y
        self.rotation_copy = 0

    def draw(self):
        """
        Draw the block from shape blocks. Each shape block
        is filled with a color and black border.
        """
        for bl in self.shape:
            pygame.draw.rect(self.screen, self.color, bl)
            pygame.draw.rect(
                self.screen, constants.BLACK, bl, constants.MESH_WIDTH
            )

    def get_rotated(self, x, y):
        """
        Compute the new coordinates based on the rotation angle.

        Parameters:
            - x - the X coordinate to transfer
            - y - the Y coordinate to transfer

        Returns the tuple with new (X,Y) coordinates.
        """
        # Use the classic transformation matrix:
        # https://en.wikipedia.org/wiki/Rotation_matrix
        rads = self.diff_rotation * (math.pi / 180.0)
        newx = round(x * math.cos(rads) - y * math.sin(rads))
        newy = round(y * math.cos(rads) + x * math.sin(rads))
        return (newx, newy)

    def move(self, x, y):
        """
        Move all elements of the block using the given offset.

        Parameters:
            - x - movement in the X coordinate
            - y - movement in the Y coordinate
        """
        # Accumulate X,Y coordinates and call the update function
        self.diffx += x
        self.diffy += y
        self._update()

    def remove_blocks(self, y):
        """
        Remove blocks on the Y coordinate. All blocks
        above the Y are moved one step down.

        Parameters:
            - y - Y coordinate to work with.
        """
        new_shape = []
        for tmp_shape in self.shape:
            if tmp_shape.y < y:
                # Block is above the y, move down and add to active shapes.
                new_shape.append(tmp_shape)
                tmp_shape.move_ip(0, constants.BHEIGHT)
            elif tmp_shape.y > y:
                # Block is below the y, add it to the list.
                new_shape.append(tmp_shape)
        # Setup the new list of block shapes.
        self.shape = new_shape

    def has_blocks(self):
        """
        Returns true if the block has some shape blocks in the shape list.
        """
        return len(self.shape) > 0

    def rotate(self):
        """
        Setup the rotation value to 90 degrees.
        """
        # Setup the rotation and update coordinates of all shape blocks.
        # The block is rotated iff the rotation is enabled
        if self.rotate_en:
            self.diff_rotation = 90
            self._update()

    def _update(self):
        """
        Update the position of all shape boxes.
        """
        for bl in self.shape:
            # Get old coordinates and compute new x,y coordinates.
            # All rotation calculations are done in the original coordinates.
            origX = (bl.x - self.x) // constants.BWIDTH
            origY = (bl.y - self.y) // constants.BHEIGHT
            rx, ry = self.get_rotated(origX, origY)
            newX = int(rx * constants.BWIDTH + self.x + self.diffx)
            newY = int(ry * constants.BHEIGHT + self.y + self.diffy)
            # Compute the relative move
            newPosX = newX - bl.x
            newPosY = newY - bl.y
            bl.move_ip(newPosX, newPosY)
        # Update coordinates and reset the move variables.
        self.x += self.diffx
        self.y += self.diffy
        self.diffx = 0
        self.diffy = 0
        self.diff_rotation = 0

    def backup(self):
        """
        Backup the current configuration of shape blocks.
        """
        self.shape_copy = copy.deepcopy(self.shape)
        self.x_copy = self.x
        self.y_copy = self.y
        self.rotation_copy = self.diff_rotation

    def restore(self):
        """
        Restore the previous configuration.
        """
        self.shape = copy.deepcopy(self.shape_copy)
        self.x = self.x_copy
        self.y = self.y_copy
        self.diff_rotation = self.rotation_copy

    def check_collision(self, rect_list):
        """
        The function checks if the block collides with any other block
        in the given list.

        Parameters:
            - rect_list - list of Rect objects used for collision detection.
        """
        for blk in rect_list:
            if blk.collidelist(self.shape) != -1:
                return True
        return False
