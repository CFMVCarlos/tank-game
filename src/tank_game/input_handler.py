"""Input handling and Command pattern implementations for player actions."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

import pygame

# Constants for action increments
VALUE_ANGLE_LEFT: float = -0.03
VALUE_ANGLE_RIGHT: float = -VALUE_ANGLE_LEFT
VALUE_MOVE_LEFT: tuple[int, int] = (-3, 0)
VALUE_MOVE_RIGHT: tuple[int, int] = (3, 0)
VALUE_POWER_DOWN: float = -1.5
VALUE_POWER_UP: float = -VALUE_POWER_DOWN


class Command(ABC):
    """Abstract base class representing an executable input command."""

    def __init__(self) -> None:
        self.actor: Any = None

    @abstractmethod
    def execute(self, actor: Any) -> None:
        """Execute the command on the target actor.

        Parameters
        ----------
        actor : Any
            The entity on which to execute this command.
        """


class AngleLeft(Command):
    """Adjust turret aim angle counter-clockwise."""

    def execute(self, actor: Any) -> None:
        """Execute angle decrease.

        Parameters
        ----------
        actor : Any
            The entity adjusting angle.
        """
        self.actor = actor
        actor.set_angle(VALUE_ANGLE_LEFT)


class AngleRight(Command):
    """Adjust turret aim angle clockwise."""

    def execute(self, actor: Any) -> None:
        """Execute angle increase.

        Parameters
        ----------
        actor : Any
            The entity adjusting angle.
        """
        self.actor = actor
        actor.set_angle(VALUE_ANGLE_RIGHT)


class PowerDown(Command):
    """Decrease firing shot velocity."""

    def execute(self, actor: Any) -> None:
        """Execute power decrease.

        Parameters
        ----------
        actor : Any
            The entity decreasing power.
        """
        self.actor = actor
        actor.set_power(VALUE_POWER_DOWN)


class PowerUp(Command):
    """Increase firing shot velocity."""

    def execute(self, actor: Any) -> None:
        """Execute power increase.

        Parameters
        ----------
        actor : Any
            The entity increasing power.
        """
        self.actor = actor
        actor.set_power(VALUE_POWER_UP)


class MoveLeft(Command):
    """Translate tank position to the left."""

    def execute(self, actor: Any) -> None:
        """Execute leftward translation.

        Parameters
        ----------
        actor : Any
            The entity moving left.
        """
        self.actor = actor
        actor.move(VALUE_MOVE_LEFT)


class MoveRight(Command):
    """Translate tank position to the right."""

    def execute(self, actor: Any) -> None:
        """Execute rightward translation.

        Parameters
        ----------
        actor : Any
            The entity moving right.
        """
        self.actor = actor
        actor.move(VALUE_MOVE_RIGHT)


class Shoot(Command):
    """Trigger bullet launch."""

    def execute(self, actor: Any) -> None:
        """Execute projectile firing.

        Parameters
        ----------
        actor : Any
            The entity firing a projectile.
        """
        self.actor = actor
        actor.shoot()


# Backward-compatible aliases
ANGLE_LEFT = AngleLeft
ANGLE_RIGHT = AngleRight
POWER_DOWN = PowerDown
POWER_UP = PowerUp
MOVE_LEFT = MoveLeft
MOVE_RIGHT = MoveRight
SHOOT = Shoot


class InputHandler:
    """Dispatches keyboard inputs to appropriate action commands."""

    def __init__(self) -> None:
        self.commands: dict[int, type[Command]] = {
            # Player 1 controls (WASD + QE + Space)
            pygame.K_q: AngleLeft,
            pygame.K_w: PowerUp,
            pygame.K_e: AngleRight,
            pygame.K_a: MoveLeft,
            pygame.K_s: PowerDown,
            pygame.K_d: MoveRight,
            pygame.K_SPACE: Shoot,
            # Player 2 controls (Arrow keys + UO / Power + Return)
            pygame.K_LEFT: MoveLeft,
            pygame.K_RIGHT: MoveRight,
            pygame.K_UP: PowerUp,
            pygame.K_DOWN: PowerDown,
            pygame.K_u: AngleLeft,
            pygame.K_o: AngleRight,
            pygame.K_RETURN: Shoot,
            # Player 2 alternative layout (IJKL)
            pygame.K_j: MoveLeft,
            pygame.K_l: MoveRight,
            pygame.K_i: PowerUp,
            pygame.K_k: PowerDown,
        }

    def update(
        self,
        events: Sequence[bool] | pygame.key.ScancodeWrapper | Any,
    ) -> dict[int, type[Command]]:
        """Map active key states to their respective command classes.

        Parameters
        ----------
        events : Sequence[bool] | pygame.key.ScancodeWrapper | Any
            Sequence or ScancodeWrapper indicating keypress states.

        Returns
        -------
        dict[int, type[Command]]
            Mapping of pressed key constants to Command classes.
        """
        active_commands: dict[int, type[Command]] = {}
        for key, cmd in self.commands.items():
            try:
                if events[key]:
                    active_commands[key] = cmd
            except (IndexError, KeyError):
                continue
        return active_commands

    def get_controls_1(self, local_player: bool = True) -> list[int]:
        """Retrieve key codes assigned to Player 1.

        Parameters
        ----------
        local_player : bool, default=True
            Whether Player 1 is controlled locally.

        Returns
        -------
        list[int]
            List of key scancodes for Player 1.
        """
        if local_player:
            return [
                pygame.K_q,
                pygame.K_w,
                pygame.K_e,
                pygame.K_a,
                pygame.K_s,
                pygame.K_d,
                pygame.K_SPACE,
            ]
        return []

    def get_controls_2(self, local_player: bool = True) -> list[int]:
        """Retrieve key codes assigned to Player 2.

        Parameters
        ----------
        local_player : bool, default=True
            Whether Player 2 is controlled locally.

        Returns
        -------
        list[int]
            List of key scancodes for Player 2.
        """
        if local_player:
            return [
                pygame.K_LEFT,
                pygame.K_RIGHT,
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_u,
                pygame.K_o,
                pygame.K_j,
                pygame.K_l,
                pygame.K_i,
                pygame.K_k,
                pygame.K_RETURN,
            ]
        return []
