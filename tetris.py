#!/usr/bin/env python3

# File: tetris.py
# Description: Main file with tetris game.
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

import math
import random
import pygame
import block
import constants


class Tetris:
    """
    The class with implementation of tetris game logic.
    """

    def __init__(self, bx, by):
        """
        Initialize the tetris object.

        Parameters:
            - bx - number of blocks in x
            - by - number of blocks in y
        """
        # Compute the resolution of the play board based on the required
        # number of blocks.
        self.resx = (bx * constants.BWIDTH + 2 * constants.BOARD_HEIGHT
                     + constants.BOARD_MARGIN)
        self.resy = (by * constants.BHEIGHT + constants.BOARD_UP_MARGIN
                     + 2 * constants.BOARD_HEIGHT + constants.BOARD_MARGIN)
        # Prepare the pygame board objects (white lines)
        self.board_up = pygame.Rect(
            0, constants.BOARD_UP_MARGIN, self.resx, constants.BOARD_HEIGHT
        )
        self.board_down = pygame.Rect(
            0, self.resy - constants.BOARD_HEIGHT, self.resx,
            constants.BOARD_HEIGHT
        )
        self.board_left = pygame.Rect(
            0, constants.BOARD_UP_MARGIN, constants.BOARD_HEIGHT,
            self.resy - constants.BOARD_UP_MARGIN
        )
        self.board_right = pygame.Rect(
            self.resx - constants.BOARD_HEIGHT, constants.BOARD_UP_MARGIN,
            constants.BOARD_HEIGHT, self.resy - constants.BOARD_UP_MARGIN
        )
        # List of used blocks
        self.blk_list = []
        # Grid start indexes for tetris blocks
        start_col = (bx - 1) // 2
        self.start_x = (constants.BOARD_HEIGHT + (constants.BOARD_MARGIN // 2)
                        + start_col * constants.BWIDTH)
        self.start_y = (constants.BOARD_UP_MARGIN + constants.BOARD_HEIGHT
                        + (constants.BOARD_MARGIN // 2))
        # Block data (shapes, colors, rotation capability). The shape is
        # encoded in the list of [X, Y] points. Each point represents the
        # relative position. The boolean value configures rotation capability.
        self.block_data = (
            ([[0, 0], [1, 0], [2, 0], [3, 0]], constants.RED, True),     # I
            ([[0, 0], [1, 0], [0, 1], [-1, 1]], constants.GREEN, True),  # S
            ([[0, 0], [1, 0], [2, 0], [2, 1]], constants.BLUE, True),    # J
            ([[0, 0], [0, 1], [1, 0], [1, 1]], constants.ORANGE, False),  # O
            ([[-1, 0], [0, 0], [0, 1], [1, 1]], constants.GOLD, True),   # Z
            ([[0, 0], [1, 0], [2, 0], [1, 1]], constants.PURPLE, True),  # T
            ([[0, 0], [1, 0], [2, 0], [0, 1]], constants.CYAN, True),    # L
        )
        self.blocks_in_line = bx
        self.blocks_in_pile = by
        # Score settings
        self.score = 0
        # Remember the current speed multiplier
        self.speed = 1.0
        # The score level threshold
        self.score_level = constants.SCORE_LEVEL
        self.active_block = None
        self.done = False
        self.game_over = False
        self.new_block = True
        self.screen = None
        self.myfont = None

    def block_collides(self):
        """
        Check if the active block collides with any other block in the game.
        """
        for blk in self.blk_list:
            if blk == self.active_block:
                continue
            if blk.check_collision(self.active_block.shape):
                return True
        return False

    def block_colides(self):
        """Alias for block_collides to maintain backward compatibility."""
        return self.block_collides()

    def is_collision(self):
        """
        Check if the active block collides with any border or existing blocks.
        """
        borders = [
            self.board_left, self.board_right, self.board_up, self.board_down
        ]
        if self.active_block.check_collision(borders):
            return True
        return self.block_collides()

    def try_move(self, dx, dy):
        """
        Attempt to move the active block by (dx, dy).
        Reverts the move and returns False if collision occurs, True otherwise.
        """
        self.active_block.backup()
        self.active_block.move(dx, dy)
        if self.is_collision():
            self.active_block.restore()
            return False
        return True

    def try_rotate(self):
        """
        Attempt to rotate the active block.
        Reverts rotation and returns False if collision occurs, True otherwise.
        """
        self.active_block.backup()
        self.active_block.rotate()
        if self.is_collision():
            self.active_block.restore()
            return False
        return True

    def step_down(self):
        """
        Move the active block down by one step. If it cannot move down,
        lock it into place, clear filled lines, and request a new block.
        """
        if not self.try_move(0, constants.BHEIGHT):
            # Check if game over (cannot move down from spawn position)
            if (self.active_block.x == self.start_x
                    and self.active_block.y == self.start_y):
                self.game_over = True
            self.detect_line()
            self.new_block = True

    def apply_action(self):
        """
        Get events from the event queue and run appropriate actions.
        """
        for ev in pygame.event.get():
            # Check if the close button was clicked or 'q' pressed.
            if ev.type == pygame.QUIT or (
                ev.type == pygame.KEYDOWN and ev.unicode == 'q'
            ):
                self.done = True
                return

            # Detect key events for game control.
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_DOWN:
                    self.step_down()
                elif ev.key == pygame.K_LEFT:
                    self.try_move(-constants.BWIDTH, 0)
                elif ev.key == pygame.K_RIGHT:
                    self.try_move(constants.BWIDTH, 0)
                elif ev.key in (pygame.K_SPACE, pygame.K_UP):
                    self.try_rotate()
                elif ev.key == pygame.K_p:
                    self.pause()

            # Movement event fired by timer.
            if ev.type == constants.TIMER_MOVE_EVENT:
                self.step_down()

    def pause(self):
        """
        Pause the game and display pause text until resumed or quit.
        """
        self.print_center(["PAUSE", 'Press "p" to continue'])
        pygame.display.flip()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (
                    ev.type == pygame.KEYDOWN and ev.unicode == 'q'
                ):
                    self.done = True
                    return
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_p:
                    return
            pygame.time.wait(20)

    def set_move_timer(self):
        """
        Setup the move timer based on current speed.
        """
        speed = math.floor(constants.MOVE_TICK / self.speed)
        speed = max(1, int(speed))
        pygame.time.set_timer(constants.TIMER_MOVE_EVENT, speed)

    def run(self):
        """
        Run the main game loop.
        """
        pygame.init()
        pygame.font.init()
        pygame.key.set_repeat(500, 50)
        self.myfont = pygame.font.Font(None, constants.FONT_SIZE)
        self.screen = pygame.display.set_mode((self.resx, self.resy))
        pygame.display.set_caption("Tetris")
        clock = pygame.time.Clock()
        self.set_move_timer()

        self.done = False
        self.game_over = False
        self.new_block = True
        self.print_status_line()

        while not self.done and not self.game_over:
            clock.tick(constants.FPS)
            self.get_block()
            if self.game_over:
                break
            self.game_logic()
            self.draw_game()

        if self.game_over:
            self.print_game_over()

        pygame.font.quit()
        pygame.display.quit()
        pygame.quit()

    def print_status_line(self):
        """
        Print the current score and speed line.
        """
        string = [f"SCORE: {self.score}   SPEED: {self.speed:g}x"]
        self.print_text(string, constants.POINT_MARGIN, constants.POINT_MARGIN)

    def print_game_over(self):
        """
        Print the game over string and wait for exit keypress.
        """
        self.print_center(["Game Over", 'Press "q" to exit'])
        pygame.display.flip()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (
                    ev.type == pygame.KEYDOWN and ev.unicode == 'q'
                ):
                    return
            pygame.time.wait(20)

    def print_text(self, str_lst, x, y):
        """
        Print text at coordinates (x, y).

        Parameters:
            - str_lst - list of strings to print. Each string on a new line.
            - x - X coordinate of the first string
            - y - Y coordinate of the first string
        """
        prev_y = 0
        for string in str_lst:
            size_x, size_y = self.myfont.size(string)
            txt_surf = self.myfont.render(string, False, constants.WHITE)
            self.screen.blit(txt_surf, (x, y + prev_y))
            prev_y += size_y

    def print_center(self, str_list):
        """
        Print strings centered horizontally and vertically on the screen.

        Parameters:
            - str_list - list of strings to print. Each string on a new line.
        """
        total_y = sum(self.myfont.size(s)[1] for s in str_list)
        start_y = (self.resy - total_y) // 2
        prev_y = 0
        for string in str_list:
            size_x, size_y = self.myfont.size(string)
            txt_surf = self.myfont.render(string, False, constants.WHITE)
            self.screen.blit(
                txt_surf, ((self.resx - size_x) // 2, start_y + prev_y)
            )
            prev_y += size_y

    def game_logic(self):
        """
        Implementation of the main game logic.
        """
        self.apply_action()

    def detect_line(self):
        """
        Detect if any lines are filled. If yes, remove them and
        move remaining building blocks down.
        """
        cleared_lines = 0
        y = self.start_y + (self.blocks_in_pile - 1) * constants.BHEIGHT
        while y >= self.start_y:
            if self.get_blocks_in_line(y) == self.blocks_in_line:
                self.remove_line(y)
                cleared_lines += 1
            else:
                y -= constants.BHEIGHT

        if cleared_lines > 0:
            self.score += (
                cleared_lines * self.blocks_in_line * constants.POINT_VALUE
            )
            while self.score >= self.score_level:
                self.score_level *= constants.SCORE_LEVEL_RATIO
                self.speed *= constants.GAME_SPEEDUP_RATIO
                self.set_move_timer()

    def remove_line(self, y):
        """
        Remove the line with given Y coordinate. Blocks below the filled
        line are untouched. Blocks above the filled line are moved down.

        Parameters:
            - y - Y coordinate of the line to remove.
        """
        for blk in self.blk_list:
            blk.remove_blocks(y)
        self.blk_list = [blk for blk in self.blk_list if blk.has_blocks()]

    def get_blocks_in_line(self, y):
        """
        Get the number of shape blocks on the given Y coordinate.

        Parameters:
            - y - Y coordinate to scan.
        """
        tmp_cnt = 0
        for blk in self.blk_list:
            for shape_block in blk.shape:
                if shape_block.y == y:
                    tmp_cnt += 1
        return tmp_cnt

    def draw_board(self):
        """
        Draw the board borders and status line.
        """
        pygame.draw.rect(self.screen, constants.WHITE, self.board_up)
        pygame.draw.rect(self.screen, constants.WHITE, self.board_down)
        pygame.draw.rect(self.screen, constants.WHITE, self.board_left)
        pygame.draw.rect(self.screen, constants.WHITE, self.board_right)
        self.print_status_line()

    def get_block(self):
        """
        Generate a new block into the game if required.
        """
        if self.new_block:
            tmp = random.randint(0, len(self.block_data) - 1)
            data = self.block_data[tmp]
            self.active_block = block.Block(
                data[0], self.start_x, self.start_y, self.screen,
                data[1], data[2]
            )
            self.blk_list.append(self.active_block)
            self.new_block = False
            if self.block_collides():
                self.game_over = True

    def draw_game(self):
        """
        Draw the game screen.
        """
        self.screen.fill(constants.BLACK)
        self.draw_board()
        for blk in self.blk_list:
            blk.draw()
        pygame.display.flip()


if __name__ == "__main__":
    Tetris(16, 30).run()
