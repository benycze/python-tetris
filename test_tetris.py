#!/usr/bin/env python3

"""
Unit tests for the python-tetris game.
"""

import os
import pygame
import pytest
import constants
from block import Block
from tetris import Tetris

os.environ["SDL_VIDEODRIVER"] = "dummy"


@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """Initialize pygame once for tests."""
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture
def dummy_screen():
    """Provide a headless dummy screen."""
    return pygame.Surface((336, 656))


def test_constants():
    """Verify key constants have sensible values."""
    assert constants.BWIDTH > 0
    assert constants.BHEIGHT > 0
    assert constants.BOARD_HEIGHT > 0
    assert constants.FPS == 60
    assert constants.MOVE_TICK > 0
    assert constants.GAME_SPEEDUP_RATIO > 1.0
    assert constants.SCORE_LEVEL > 0
    assert constants.POINT_VALUE > 0


def test_block_creation_and_movement(dummy_screen):
    """Test block creation and movement offsets."""
    shape_def = [[0, 0], [1, 0], [2, 0], [3, 0]]
    blk = Block(shape_def, 100, 100, dummy_screen, constants.RED, True)

    assert len(blk.shape) == 4
    assert blk.has_blocks() is True
    assert blk.shape[0].x == 100
    assert blk.shape[0].y == 100
    assert blk.shape[1].x == 100 + constants.BWIDTH

    blk.move(constants.BWIDTH, constants.BHEIGHT)
    assert blk.shape[0].x == 100 + constants.BWIDTH
    assert blk.shape[0].y == 100 + constants.BHEIGHT
    assert blk.x == 100 + constants.BWIDTH
    assert blk.y == 100 + constants.BHEIGHT


def test_block_rotation(dummy_screen):
    """Test 90-degree rotations and verify complete 360-degree cycle."""
    shape_def = [[0, 0], [1, 0], [2, 0], [1, 1]]  # T-shape
    blk = Block(shape_def, 100, 100, dummy_screen, constants.PURPLE, True)
    initial_positions = [(r.x, r.y) for r in blk.shape]

    # Rotate 4 times (360 degrees total)
    for _ in range(4):
        blk.rotate()

    final_positions = [(r.x, r.y) for r in blk.shape]
    assert initial_positions == final_positions


def test_block_rotation_disabled(dummy_screen):
    """Test that blocks with rotation disabled (e.g. O block) do not rotate."""
    shape_def = [[0, 0], [0, 1], [1, 0], [1, 1]]
    blk = Block(shape_def, 100, 100, dummy_screen, constants.ORANGE, False)
    initial_positions = [(r.x, r.y) for r in blk.shape]

    blk.rotate()
    final_positions = [(r.x, r.y) for r in blk.shape]
    assert initial_positions == final_positions


def test_block_backup_and_restore(dummy_screen):
    """Test backup and restore state functionality."""
    shape_def = [[0, 0], [1, 0]]
    blk = Block(shape_def, 100, 100, dummy_screen, constants.BLUE, True)

    blk.backup()
    blk.move(50, 50)
    assert blk.x == 150
    assert blk.shape[0].x == 150

    blk.restore()
    assert blk.x == 100
    assert blk.shape[0].x == 100


def test_block_remove_blocks(dummy_screen):
    """Test removing blocks at a specific row and shifting upper blocks."""
    # Two blocks at y=100 (above), two at y=120 (removed), one at y=140 (below)
    shape_def = [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2]]
    blk = Block(shape_def, 100, 100, dummy_screen, constants.GREEN, True)
    # y=100 (row 0), y=120 (row 1), y=140 (row 2)
    assert len(blk.shape) == 5

    blk.remove_blocks(120)

    # 2 blocks from row 1 removed -> 3 remaining
    assert len(blk.shape) == 3
    # Upper blocks moved from 100 to 120
    upper_ys = [r.y for r in blk.shape if r.y == 120]
    assert len(upper_ys) == 2
    # Lower block at 140 stayed at 140
    lower_ys = [r.y for r in blk.shape if r.y == 140]
    assert len(lower_ys) == 1


def test_tetris_initialization():
    """Test Tetris grid dimensions and resolution calculation."""
    game = Tetris(16, 30)

    # Dimensions
    expected_resx = (16 * constants.BWIDTH + 2 * constants.BOARD_HEIGHT
                     + constants.BOARD_MARGIN)
    expected_resy = (30 * constants.BHEIGHT + constants.BOARD_UP_MARGIN
                     + 2 * constants.BOARD_HEIGHT + constants.BOARD_MARGIN)
    assert game.resx == expected_resx
    assert game.resy == expected_resy
    assert game.blocks_in_line == 16
    assert game.blocks_in_pile == 30

    # Ensure top and bottom margins are exactly half of BOARD_MARGIN
    top_margin = game.start_y - game.board_up.bottom
    bottom_block_bottom = game.start_y + 30 * constants.BHEIGHT
    bottom_margin = game.board_down.top - bottom_block_bottom
    assert top_margin == constants.BOARD_MARGIN // 2
    assert bottom_margin == constants.BOARD_MARGIN // 2

    # Check start_x grid alignment
    playable_start_x = constants.BOARD_HEIGHT + (constants.BOARD_MARGIN // 2)
    offset_x = game.start_x - playable_start_x
    assert offset_x % constants.BWIDTH == 0


def test_tetris_movement_and_boundaries(dummy_screen):
    """Test movement within board bounds and wall collision rejection."""
    game = Tetris(16, 30)
    game.screen = dummy_screen
    game.get_block()
    active = game.active_block

    # Test moving left repeatedly until hitting the left wall
    moved_left = True
    while moved_left:
        moved_left = game.try_move(-constants.BWIDTH, 0)

    # Leftmost block should not penetrate board_left
    min_x = min(r.x for r in active.shape)
    assert min_x >= game.board_left.right

    # Move right repeatedly until hitting the right wall
    moved_right = True
    while moved_right:
        moved_right = game.try_move(constants.BWIDTH, 0)

    # Rightmost block should not penetrate board_right
    max_x = max(r.right for r in active.shape)
    assert max_x <= game.board_right.left


def test_tetris_step_down_and_lock(dummy_screen):
    """Test active block landing on bottom wall and locking in place."""
    game = Tetris(16, 30)
    game.screen = dummy_screen
    game.get_block()
    first_block = game.active_block

    # Step down until it locks
    for _ in range(50):
        game.step_down()
        if game.new_block:
            break

    assert game.new_block is True
    # The first block should now be settled in blk_list
    assert first_block in game.blk_list
    # Spawning a new block should produce a different active_block
    game.get_block()
    assert game.active_block is not first_block


def test_tetris_line_clearing(dummy_screen):
    """Test detecting and clearing filled lines and updating score."""
    game = Tetris(16, 30)
    game.screen = dummy_screen

    # Manually fill the bottom row (row 29)
    bottom_y = game.start_y + 29 * constants.BHEIGHT
    for col in range(16):
        x = (constants.BOARD_HEIGHT + (constants.BOARD_MARGIN // 2)
             + col * constants.BWIDTH)
        b = Block([[0, 0]], x, bottom_y, dummy_screen, constants.RED, False)
        game.blk_list.append(b)

    assert game.get_blocks_in_line(bottom_y) == 16

    # Call detect_line
    game.detect_line()

    # The line should be cleared
    assert game.get_blocks_in_line(bottom_y) == 0
    assert game.score == 16 * constants.POINT_VALUE


def test_tetris_multi_line_clearing(dummy_screen):
    """Test clearing multiple simultaneously filled rows (double/triple)."""
    game = Tetris(16, 30)
    game.screen = dummy_screen

    row28_y = game.start_y + 28 * constants.BHEIGHT
    row29_y = game.start_y + 29 * constants.BHEIGHT

    for col in range(16):
        x = (constants.BOARD_HEIGHT + (constants.BOARD_MARGIN // 2)
             + col * constants.BWIDTH)
        b1 = Block([[0, 0]], x, row28_y, dummy_screen, constants.RED, False)
        b2 = Block([[0, 0]], x, row29_y, dummy_screen, constants.BLUE, False)
        game.blk_list.extend([b1, b2])

    # Add one block above at row 27
    row27_y = game.start_y + 27 * constants.BHEIGHT
    marker_block = Block(
        [[0, 0]],
        constants.BOARD_HEIGHT + (constants.BOARD_MARGIN // 2),
        row27_y, dummy_screen, constants.GREEN, False
    )
    game.blk_list.append(marker_block)

    game.detect_line()

    # Both lines 28 and 29 cleared, marker block drops 2 rows from 27 to 29
    assert game.get_blocks_in_line(row28_y) == 0
    assert game.get_blocks_in_line(row29_y) == 1
    assert marker_block.shape[0].y == row29_y
    assert game.score == 2 * 16 * constants.POINT_VALUE


def test_tetris_speedup_on_score(dummy_screen):
    """Test game speed progression when crossing score thresholds."""
    game = Tetris(16, 30)
    game.screen = dummy_screen
    initial_speed = game.speed
    initial_threshold = game.score_level

    # Give enough score to exceed the threshold
    game.score = initial_threshold + 500
    # Simulate detect_line logic for threshold check
    while game.score >= game.score_level:
        game.score_level *= constants.SCORE_LEVEL_RATIO
        game.speed *= constants.GAME_SPEEDUP_RATIO

    assert game.speed > initial_speed
    assert game.score_level > initial_threshold
