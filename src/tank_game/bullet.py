"""Bullet projectile physics, trajectory, and collision state."""

import math


class Bullet:
    """Manages bullet motion, ballistic physics, and collision parameters.

    Parameters
    ----------
    pos : tuple[int, int]
        Initial (x, y) coordinates for the bullet.
    """

    def __init__(self, pos: tuple[int, int]) -> None:
        self.pos: tuple[float, float] = (float(pos[0]), float(pos[1]))
        self.last_pos: tuple[float, float] = self.pos
        self.bullet_hit_position: tuple[int, int] = (int(pos[0]), int(pos[1]))
        self.shooting: bool = False
        self.power: float = 0.0
        self.angle: float = 0.0
        self.gravity: tuple[float, float] = (0.0, 0.98)
        self.velocity: tuple[float, float] = (0.0, 0.0)

    def shoot(
        self,
        pos: tuple[int, int],
        angle: float = -math.pi / 4,
        power: float = 50.0,
    ) -> None:
        """Reset bullet ballistic parameters and initiate flight.

        Parameters
        ----------
        pos : tuple[int, int]
            Origin (x, y) coordinates from the firing tank.
        angle : float, default=-math.pi / 4
            Launch angle in radians.
        power : float, default=50.0
            Firing power magnitude.
        """
        self.pos = (float(pos[0]), float(pos[1]))
        self.last_pos = self.pos
        self.shooting = True
        self.angle = angle
        self.power = power * 0.75
        self.velocity = (
            self.power * math.cos(self.angle),
            self.power * math.sin(self.angle),
        )

    def update(self) -> None:
        """Update bullet ballistic trajectory according to velocity and gravity."""
        if self.shooting:
            self.last_pos = self.pos
            self.velocity = (
                self.velocity[0] + self.gravity[0],
                self.velocity[1] + self.gravity[1],
            )
            self.pos = (
                self.pos[0] + self.velocity[0],
                self.pos[1] + self.velocity[1],
            )

    def set_pos(self, pos: tuple[int, int]) -> None:
        """Update the bullet position directly when docked to a tank.

        Parameters
        ----------
        pos : tuple[int, int]
            New coordinates for the bullet.
        """
        self.pos = (float(pos[0]), float(pos[1]))

    def set_bullet_hit_position(self, pos: tuple[int, int]) -> None:
        """Record the point of impact when a collision occurs.

        Parameters
        ----------
        pos : tuple[int, int]
            Impact coordinates (x, y).
        """
        self.bullet_hit_position = (int(pos[0]), int(pos[1]))
