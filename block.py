#!/usr/bin/env python3

import pdb

import constants
import block
import pygame
import math
import copy
import sys

class Block(object):
    """
    Abstract class for the implementation of the object
    """    

    def __init__(self,shape,x,y,screen,color):
        """
        The x, y defines the left top corner of the building block
        """
        # The initial shape (convert all to Rects)
        self.shape = []
        for sh in shape:
            bx = sh[0]*constants.BWIDTH + x
            by = sh[1]*constants.BHEIGHT + y
            block = pygame.Rect(bx,by,constants.BWIDTH,constants.BHEIGHT)
            self.shape.append(block)     
        # Setup the rest of variables
        self.x = x
        self.y = y
        self.diffx = 0
        self.diffy = 0
        self.screen = screen
        self.color = color
        self.diff_rotation = 0
        self.max_y = -1

    def draw(self):
        """
        Draw the block
        """
        for bl in self.shape:
            pygame.draw.rect(self.screen,self.color,bl,5)
        
    def get_rotated(self,x,y):
        """
        Compute the new coordinates based on the rotation angle.

        Returns the tuple with new x,y coordinates
        """
        # Use the classic transformation matrix:
        # https://www.siggraph.org/education/materials/HyperGraph/modeling/mod_tran/2drota.htm
        rads = self.diff_rotation * (math.pi / 180.0)
        newx = x*math.cos(rads) - y*math.sin(rads)
        newy = y*math.cos(rads) + x*math.sin(rads)
        return (newx,newy)        

    def move(self,x,y):
        """
        Move the center of the block to the X,Y 
        """       
        self.diffx += x
        self.diffy += y  
        self._update()

    def rotate(self):
        """
        Setup the rotation value to 90 degrees
        """
        self.diff_rotation = 90
        self._update()

    def _update(self):
        """
        Update the position of boxes
        """
        self.max_y = -1
        for bl in self.shape:
            # Compute get old indexes and compute the new x,y indicies
            origX = (bl.x - self.x)/constants.BWIDTH
            origY = (bl.y - self.y)/constants.BHEIGHT
            rx,ry = self.get_rotated(origX,origY)
            newX = rx*constants.BWIDTH  + self.x + self.diffx
            newY = ry*constants.BHEIGHT + self.y + self.diffy
            # Compute the relative move
            newPosX = newX - bl.x
            newPosY = newY - bl.y
            bl.move_ip(newPosX,newPosY)
            self.max_y = max(self.max_y,newY)
        # Everyhting was moved, disable, remember new x,y
        self.x += self.diffx
        self.y += self.diffy
        # Reset control variables
        self.diffx = 0
        self.diffy = 0
        self.diff_rotation = 0

    def backup(self):
        """
        Backup the current configuration of blocks
        """
        self.shape_copy = copy.deepcopy(self.shape)
        self.x_copy = self.x
        self.y_copy = self.y
        self.rotation_copy = self.diff_rotation     

    def restore(self):
        """
        Restore the previous configuraiton
        """
        self.shape = self.shape_copy
        self.x = self.x_copy
        self.y = self.y_copy
        self.diff_rotation = self.rotation_copy

    def check_collision(self,blk_list):
        """
        Check if the block colides with any block
        in the shape list. The function accepts a list of 
        Rect objects.
        """
        for blk in blk_list:
            collist = blk.collidelistall(self.shape)
            if len(collist):
                return True
        return False

    def get_max_blocks(self):
        """
        Return the blocks which has maximal Y coordinate (for detection
        of lower colisions)
        """ 
        return [blk for blk in self.shape if blk.y == self.max_y]

