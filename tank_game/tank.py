"""Tank combatant entity, attributes, physics, and state dispatching."""

import math
from collections.abc import Sequence

from tank_game.bullet import Bullet
from tank_game.fsm import FSM, STATES, TRANSITIONS, Event
from tank_game.input_handler import Command, InputHandler, Shoot


class Tank:
    """Represents an armed combat tank in the battlefield.

    Parameters
    ----------
    pos : tuple[int, int]
        Initial (x, y) coordinates on the battlefield.
    controls : int, optional
        Control scheme identifier (1 for Player 1, 2 for Player 2), default is 1.
    """

    def __init__(self, pos: tuple[int, int], controls: int = 1) -> None:
        self.name: str = f"Tank {controls}"
        self.max_health: int = 100
        self.health: float = float(self.max_health)
        self.pos: tuple[int, int] = pos
        self.center_pos: tuple[int, int] = pos
        self.bullet: Bullet = Bullet(self.pos)
        self.bullet_angle: float = -math.pi / 4
        self.bullet_power: float = 50.0
        self.fsm: FSM = FSM(STATES, TRANSITIONS)
        self.IH: InputHandler = InputHandler()
        self.controls: int = controls
        self.current_player: bool = False
        self.bulletHit: bool = False
        self.local_player: bool = False
        self.commands: dict[int, type[Command]] = {}

    def set_local_player(self, state: bool) -> None:
        """Configure whether the tank is controlled by the local machine.

        Parameters
        ----------
        state : bool
            True if local, False if remote peer.
        """
        self.local_player = state

    def set_pos(self, pos: tuple[int, int]) -> "Tank":
        """Update top-left position coordinates of the tank.

        Parameters
        ----------
        pos : tuple[int, int]
            New (x, y) screen position.

        Returns
        -------
        Tank
            The updated tank instance.
        """
        self.pos = pos
        return self

    def set_controls(self, controls: int) -> "Tank":
        """Set the control layout identifier for player mapping.

        Parameters
        ----------
        controls : int
            Control index (1 or 2).

        Returns
        -------
        Tank
            The updated tank instance.
        """
        self.controls = controls
        return self

    def get_controls(self) -> list[int]:
        """Retrieve the key bindings configured for this tank.

        Returns
        -------
        list[int]
            List of active key scancodes.
        """
        if self.controls == 1:
            return self.IH.get_controls_1()
        return self.IH.get_controls_2()

    def move(self, direction: tuple[int, int]) -> None:
        """Translate the tank position and keep its docked bullet synchronized.

        Parameters
        ----------
        direction : tuple[int, int]
            Delta movement offset (dx, dy).
        """
        self.pos = (self.pos[0] + direction[0], self.pos[1] + direction[1])
        self.bullet.set_pos(self.center_pos)

    def shoot(self) -> None:
        """Discharge the tank bullet using current angle and power."""
        self.bullet.shoot(self.center_pos, self.bullet_angle, self.bullet_power)

    def update(self, events: Sequence[bool]) -> bool:
        """Process player inputs, update internal FSM, and trigger actions.

        Parameters
        ----------
        events : Sequence[bool]
            Key state booleans indexed by key scancode.

        Returns
        -------
        bool
            True if entity remains active, False if destroyed.
        """
        self.commands = self.IH.update(events)
        event: Event | None = None

        if self.bulletHit:
            event = Event.IDLE
        elif self.health <= 0:
            event = Event.DESTROYED
        else:
            if self.current_player:
                event = Event.MOVING
            if any(issubclass(cmd, Shoot) for cmd in self.commands.values()):
                event = Event.FIRING
            if self.bullet.shooting:
                event = Event.RELOADING

        return self.fsm.update(event=event, actor=self)

    def set_center_pos(self, pos: tuple[int, int]) -> None:
        """Update center coordinates for firing calculations.

        Parameters
        ----------
        pos : tuple[int, int]
            Center position (cx, cy).
        """
        self.center_pos = pos

    def set_angle(self, angle: float) -> None:
        """Adjust and clamp turret aiming angle.

        Parameters
        ----------
        angle : float
            Delta angle in radians.
        """
        self.bullet_angle += angle
        if self.bullet_angle > 0.0:
            self.bullet_angle = 0.0
        elif self.bullet_angle < -math.pi:
            self.bullet_angle = -math.pi

    def set_power(self, power: float) -> None:
        """Adjust and clamp firing power.

        Parameters
        ----------
        power : float
            Delta power adjustment.
        """
        self.bullet_power += power
        if self.bullet_power > 100.0:
            self.bullet_power = 100.0
        elif self.bullet_power < 0.0:
            self.bullet_power = 0.0

    def calculate_damage(
        self,
        bullet_pos: tuple[int, int],
        bullet_type: int = 0,
    ) -> float:
        """Calculate and apply splash damage from an exploding projectile.

        Parameters
        ----------
        bullet_pos : tuple[int, int]
            Coordinates of projectile impact.
        bullet_type : int, optional
            Ammunition type identifier, default is 0.

        Returns
        -------
        float
            Total damage points deducted from health.
        """
        _ = bullet_type
        dist = self.distance(bullet_pos, self.center_pos)
        damage_coefficient: float = 500.0
        max_damage: float = 40.0
        max_blast_radius: float = 50.0

        if dist > max_blast_radius:
            damage = 0.0
        elif dist <= 1.0:
            damage = max_damage
        else:
            damage = min(
                (1.0 / (dist * dist)) * damage_coefficient * max_damage,
                max_damage,
            )

        self.health = max(0.0, self.health - damage)
        return damage

    @staticmethod
    def distance(coord1: tuple[int, int], coord2: tuple[int, int]) -> float:
        """Compute Euclidean distance between two 2D points.

        Parameters
        ----------
        coord1 : tuple[int, int]
            First coordinate pair (x1, y1).
        coord2 : tuple[int, int]
            Second coordinate pair (x2, y2).

        Returns
        -------
        float
            Euclidean distance.
        """
        return math.dist(coord1, coord2)

    def set_tank_name(self, name: str) -> "Tank":
        """Assign customized display name to the tank.

        Parameters
        ----------
        name : str
            Display name string.

        Returns
        -------
        Tank
            The updated tank instance.
        """
        self.name = name
        return self

    def clone(self) -> "Tank":
        """Create an independent copy of this tank prototype.

        Returns
        -------
        Tank
            Fresh tank instance at same initial position.
        """
        return Tank(self.pos, self.controls)


class TankSpawner:
    """Spawns configured tanks from prototype templates."""

    @staticmethod
    def spawn_tank(prototype: Tank) -> Tank:
        """Instantiate a new tank cloning prototype properties.

        Parameters
        ----------
        prototype : Tank
            The template tank instance.

        Returns
        -------
        Tank
            A newly initialized clone.
        """
        return prototype.clone()


# Backward-compatible alias
Tank_Spawner = TankSpawner
