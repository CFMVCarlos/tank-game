"""Visual particle effects system for explosions, impacts, and sparks."""

import math
import random
from collections.abc import Sequence

import pygame

from tank_game import colors


class Particle:
    """Represents an individual physical particle with decay and gravity.

    Parameters
    ----------
    x : float
        Horizontal origin coordinate.
    y : float
        Vertical origin coordinate.
    color : tuple[int, int, int]
        RGB base color.
    velocity : tuple[float, float]
        Initial velocity vector (vx, vy).
    radius : float
        Initial particle size.
    lifetime : int
        Maximum lifespan in animation ticks.
    """

    def __init__(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int],
        velocity: tuple[float, float],
        radius: float = 3.0,
        lifetime: int = 25,
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.color: tuple[int, int, int] = color
        self.vx: float = velocity[0]
        self.vy: float = velocity[1]
        self.radius: float = radius
        self.lifetime: int = lifetime
        self.age: int = 0

    @property
    def alive(self) -> bool:
        """Check whether particle has remaining life.

        Returns
        -------
        bool
            True if age is less than lifetime; otherwise False.
        """
        return self.age < self.lifetime

    def update(self) -> None:
        """Advance physical simulation and age the particle."""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity acceleration
        self.vx *= 0.96  # Air friction
        self.age += 1
        self.radius = max(0.5, self.radius * 0.94)

    def draw(self, surface: pygame.Surface) -> None:
        """Render particle onto target surface.

        Parameters
        ----------
        surface : pygame.Surface
            Target Pygame canvas.
        """
        if self.alive and self.radius > 0.5:
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                int(self.radius),
            )


class ParticleManager:
    """Manages active particle pools and triggers specialized emission bursts."""

    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def spawn_explosion_burst(
        self,
        pos: tuple[int, int],
        count: int = 30,
    ) -> None:
        """Spawn a radial burst of fire and smoke particles upon impact.

        Parameters
        ----------
        pos : tuple[int, int]
            Origin (x, y) coordinates of impact.
        count : int, optional
            Number of particles emitted, default is 30.
        """
        palette: Sequence[tuple[int, int, int]] = (
            colors.GOLD,
            colors.ORANGE,
            colors.RED,
            colors.WHITE,
            colors.DARK_GRAY,
        )
        for _ in range(count):
            speed = random.uniform(2.0, 7.0)
            angle = random.uniform(0.0, math.tau)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle) - 1.0
            color = random.choice(palette)
            lifetime = random.randint(18, 40)
            radius = random.uniform(2.0, 4.5)
            self.particles.append(
                Particle(
                    float(pos[0]),
                    float(pos[1]),
                    color,
                    (vx, vy),
                    radius,
                    lifetime,
                )
            )

    def spawn_spark_trail(self, pos: tuple[int, int]) -> None:
        """Emit small sparks trailing behind a high-velocity projectile.

        Parameters
        ----------
        pos : tuple[int, int]
            Current projectile coordinates (x, y).
        """
        for _ in range(2):
            vx = random.uniform(-1.0, 1.0)
            vy = random.uniform(-1.0, 1.0)
            self.particles.append(
                Particle(
                    float(pos[0]),
                    float(pos[1]),
                    colors.GOLD,
                    (vx, vy),
                    radius=1.5,
                    lifetime=10,
                )
            )

    def update(self) -> None:
        """Update physics for all active particles and remove expired ones."""
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all living particles to screen.

        Parameters
        ----------
        surface : pygame.Surface
            Target display surface.
        """
        for p in self.particles:
            p.draw(surface)
