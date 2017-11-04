#!/usr/bin/env python3

from pygame.locals import *

# Width of the box
BWIDTH   = 20
BHEIGHT  = 20

# Board configuration
BOARD_HEIGHT     = 7
BOARD_UP_MARGIN  = 35

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
