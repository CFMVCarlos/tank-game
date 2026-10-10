# Standard library imports
import math


class Bullet:
    def __init__(self, pos: tuple[int, int]) -> None:
        # Set the acceleration due to gravity
        self.gravity: float = 9.81 * 10
        # Set the initial x and y position of the bullet
        self.pos: tuple[int, int] = pos
        # Set the time step (how often the bullet position is updated)
        self.time_step: float = 0.02
        # Set the initial time
        self.time: float = 0
        # Set flag to identify bullet is moving or stopped
        self.shooting: bool = False
        # Define bullet last position
        self.last_pos: tuple[int, int] = self.pos
        # Define bullets hit point
        self.bullet_hit_position: tuple[int, int] = self.pos
        # Set bullet angle
        self.angle: float = 0
        # Set bullet power
        self.power: float = 0
        # Set initial velocity
        self.velocity: tuple[float, float] = (0, 0)

    def shoot(
        self,
        pos: tuple[int, int],
        angle: float = -math.pi / 4,
        power: float = 50,
    ) -> None:
        """Function to reset bullets parameters to be ready to be shot."""
        # Redefine bullet to position to tank's position
        self.pos = pos
        # Redefine bullet last position to tank's position
        self.last_pos = pos
        # Bullet is now on the move
        self.shooting = True
        # Reset time bullet is on air
        self.time = 0
        # Set bullet angle
        self.angle: float = angle
        # Set bullet power
        self.power: float = power * 0.75
        # Set initial velocity
        self.velocity: tuple[float, float] = (
            self.power * math.cos(self.angle),
            self.power * math.sin(self.angle),
        )

    def update(self) -> None:
        """Updates the bullets position according to angle, power and gravity while bullet is on air."""
        if self.shooting:
            # Update bullet's last position
            self.last_pos = self.pos
            # Increase the time
            self.time += self.time_step
            # Update the x and y position of the bullet
            self.pos = (
                self.pos[0] + self.velocity[0] * self.time + 0.5 * 0 * self.time**2,
                self.pos[1]
                + self.velocity[1] * self.time
                + 0.5 * self.gravity * self.time**2,
            )

    def set_bullet_hit_position(self, tank_hit=False, pos=None) -> None:
        """Updates bullet's hit position."""
        # Update bullet last position to new position when bullet hits terrain
        if pos:
            self.bullet_hit_position = pos
        # If bullet hits any tank, then update to last bullet position
        elif tank_hit:
            self.bullet_hit_position = self.pos

    def set_pos(self, pos) -> None:
        """Updates bullet's position."""
        # Update bullet position
        self.pos = pos
