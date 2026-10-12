"""Unit tests for input handling and command dispatch."""

import pygame

from tank_game.input_handler import (
    AngleLeft,
    AngleRight,
    InputHandler,
    MoveLeft,
    MoveRight,
    PowerDown,
    PowerUp,
    Shoot,
)
from tank_game.tank import Tank


def test_input_handler_mappings():
    ih = InputHandler()
    assert ih.commands[pygame.K_SPACE] == Shoot
    assert ih.commands[pygame.K_a] == MoveLeft
    assert ih.commands[pygame.K_d] == MoveRight
    assert ih.commands[pygame.K_w] == PowerUp
    assert ih.commands[pygame.K_s] == PowerDown
    assert ih.commands[pygame.K_q] == AngleLeft
    assert ih.commands[pygame.K_e] == AngleRight


def test_commands_execution():
    tank = Tank((100, 100))
    tank.set_center_pos((100, 100))

    MoveRight().execute(tank)
    assert tank.pos[0] == 101

    MoveLeft().execute(tank)
    assert tank.pos[0] == 100

    PowerUp().execute(tank)
    assert tank.bullet_power > 50.0

    PowerDown().execute(tank)
    assert tank.bullet_power == 50.0
