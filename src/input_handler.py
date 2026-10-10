from typing import Never

import pygame

# Constants representing the values that will be added to the angle or power of the bullet, or the movement of the tank
VALUE_ANGLE_LEFT: float = -0.01
VALUE_ANGLE_RIGHT: float = -VALUE_ANGLE_LEFT
VALUE_MOVE_LEFT: tuple[int, int] = (-1, 0)
VALUE_MOVE_RIGHT: tuple[int, int] = (-VALUE_MOVE_LEFT[0], VALUE_MOVE_LEFT[1])
VALUE_POWER_DOWN: float = -0.5
VALUE_POWER_UP: float = -VALUE_POWER_DOWN


class Command:
    def __init__(self) -> None:
        self.actor = None

    # Abstract method that needs to be implemented in subclasses
    def execute(self, actor) -> None:
        raise NotImplementedError


# Class representing the input handler, responsible for handling the user's inputs and returning the corresponding commands


class InputHandler:
    def __init__(self) -> None:
        # Dictionary with the key corresponding to a pygame key constant and the value being the command to be executed
        self.commands: dict[int, type[Command]] = {
            pygame.K_q: ANGLE_LEFT,
            pygame.K_w: POWER_UP,
            pygame.K_e: ANGLE_RIGHT,
            pygame.K_a: MOVE_LEFT,
            pygame.K_s: POWER_DOWN,
            pygame.K_d: MOVE_RIGHT,
            pygame.K_u: ANGLE_LEFT,
            pygame.K_i: POWER_UP,
            pygame.K_o: ANGLE_RIGHT,
            pygame.K_j: MOVE_LEFT,
            pygame.K_k: POWER_DOWN,
            pygame.K_l: MOVE_RIGHT,
            pygame.K_SPACE: SHOOT,
        }

    def update(self, events: list[bool]) -> dict[int, type[Command]]:
        """Returns a dictionary with the keys being the pygame key constants and the values being the commands to be executed, based on the events passed as parameter."""
        return {key: value for key, value in self.commands.items() if events[key]}

    def get_controls_1(self, local_player: bool = True) -> list[int]:
        """Returns a list with the keys representing the controls for player 1."""
        if local_player:
            return [
                pygame.K_q,
                pygame.K_w,
                pygame.K_e,
                pygame.K_a,
                pygame.K_s,
                pygame.K_d,
            ]
        return []

    def get_controls_2(self, local_player: bool = True) -> list[int]:
        """Returns a list with the keys representing the controls for player 2."""
        if local_player:
            return [
                pygame.K_u,
                pygame.K_i,
                pygame.K_o,
                pygame.K_j,
                pygame.K_k,
                pygame.K_l,
            ]
        return []


class ANGLE_LEFT(Command):
    def execute(self, actor) -> None:
        # Save reference to actor
        self.actor = actor
        # Call set_angle method on actor with VALUE_ANGLE_LEFT as parameter
        actor.set_angle(VALUE_ANGLE_LEFT)


class ANGLE_RIGHT(Command):
    def execute(self, actor) -> None:
        # Save reference to actor
        self.actor = actor
        # Call set_angle method on actor with VALUE_ANGLE_RIGHT as parameter
        actor.set_angle(VALUE_ANGLE_RIGHT)


class POWER_DOWN(Command):
    def execute(self, actor) -> None:
        # Save reference to actor
        self.actor = actor
        # Call set_power method on actor with VALUE_POWER_DOWN as parameter
        actor.set_power(VALUE_POWER_DOWN)


class POWER_UP(Command):
    def execute(self, actor) -> None:
        # Save reference to actor
        self.actor = actor
        # Call set_power method on actor with VALUE_POWER_UP as parameter
        actor.set_power(VALUE_POWER_UP)


class MOVE_LEFT(Command):
    def execute(self, actor) -> None:
        """Move the actor to the left."""
        # Save reference to actor
        self.actor = actor
        # Call move method on actor with VALUE_MOVE_LEFT as parameter
        actor.move(VALUE_MOVE_LEFT)


class MOVE_RIGHT(Command):
    def execute(self, actor) -> None:
        """Move the actor to the right."""
        # Save reference to actor
        self.actor = actor
        # Call move method on actor with VALUE_MOVE_RIGHT as parameter
        actor.move(VALUE_MOVE_RIGHT)


class SHOOT(Command):
    def execute(self, actor) -> None:
        """Make the actor shoot a bullet."""
        # Save reference to actor
        self.actor = actor
        # Call shoot method on actor
        actor.shoot()
