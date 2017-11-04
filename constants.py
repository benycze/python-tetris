#!/usr/bin/env python3

# File: constants.py 
# Description: Basic program constants
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


from pygame.locals import *

# Width of the box
BWIDTH   = 20
BHEIGHT  = 20

# Board configuration
BOARD_HEIGHT     = 7
BOARD_UP_MARGIN  = 35
BOARD_MARGIN     = 2

# Colors
WHITE    = (255,255,255)
RED      = (255,0,0)
GREEN    = (0,255,0)
BLUE     = (0,0,255)
ORANGE   = (255,69,0)
GOLD     = (255,125,0)
PURPLE   = (128,0,128)
CYAN     = (0,255,255) 

# Timing constraints
MOVE_TICK          = 1000
TIMER_MOVE_EVENT   = USEREVENT+1

# Font configuration
FONT_SIZE  = 40
