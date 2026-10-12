"""Finite State Machine (FSM) implementation for entity state management."""

from enum import Enum
from typing import Any


class State:
    """Base class for FSM state representations.

    Parameters
    ----------
    name : str, optional
        The human-readable name of the state, default is "".
    """

    def __init__(self, name: str = "") -> None:
        self.name: str = name or self.__class__.__name__

    def update(self, actor: Any) -> None:
        """Update the state of the entity.

        Parameters
        ----------
        actor : Any
            The entity executing this state logic.
        """


class Transition:
    """Defines a transition from one state to a target state.

    Parameters
    ----------
    from_state : type[State]
        The source state class from which transition occurs.
    to_state : type[State]
        The destination state class transitioned into.
    """

    def __init__(
        self,
        from_state: type[State],
        to_state: type[State],
    ) -> None:
        self._from: type[State] = from_state
        self._to: type[State] = to_state

    @property
    def from_state(self) -> type[State]:
        """Get the source state class.

        Returns
        -------
        type[State]
            The state class transitioned from.
        """
        return self._from

    @property
    def to_state(self) -> type[State]:
        """Get the destination state class.

        Returns
        -------
        type[State]
            The state class transitioned to.
        """
        return self._to


class Event(Enum):
    """Enumeration representing events triggering state transitions."""

    IDLE = 1
    MOVING = 2
    FIRING = 3
    RELOADING = 4
    DESTROYED = 5


class Idle(State):
    """State representing an idle tank waiting for its turn."""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    def update(self, actor: Any) -> None:
        """Reset bullet and turn flags when tank is idle.

        Parameters
        ----------
        actor : Any
            The tank entity being updated.
        """
        actor.bullet.set_pos(actor.center_pos)
        actor.bulletHit = False
        actor.bullet.shooting = False
        actor.current_player = False


class Moving(State):
    """State representing a tank actively receiving and executing movement commands."""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    def update(self, actor: Any) -> None:
        """Process movement and aiming commands for the active player.

        Parameters
        ----------
        actor : Any
            The tank entity executing commands.
        """
        controls = actor.get_controls()
        for key, cmd_type in actor.commands.items():
            if key in controls:
                cmd_type().execute(actor)


class Firing(State):
    """State representing bullet discharge trigger."""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    def update(self, actor: Any) -> None:
        """Trigger tank shooting method.

        Parameters
        ----------
        actor : Any
            The tank entity firing.
        """
        actor.shoot()


class Reloading(State):
    """State representing projectile flight time before next turn."""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    def update(self, actor: Any) -> None:
        """Advance projectile ballistic physics.

        Parameters
        ----------
        actor : Any
            The tank entity whose bullet is in flight.
        """
        actor.bullet.update()


class Destroyed(State):
    """State representing an eradicated tank entity."""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    def update(self, actor: Any) -> None:
        """Hold state upon entity destruction.

        Parameters
        ----------
        actor : Any
            The destroyed tank entity.
        """


class FSM:
    """Finite State Machine manager controlling transitions and current state.

    Parameters
    ----------
    states : list[type[State]]
        List of registered state classes.
    transitions : dict[Event, list[Transition]]
        Mapping of events to available transition rules.
    """

    def __init__(
        self,
        states: list[type[State]],
        transitions: dict[Event, list[Transition]],
    ) -> None:
        self._states: list[type[State]] = states
        self._transitions: dict[Event, list[Transition]] = transitions
        self.current: State = self._states[0]()
        self.end_type: type[State] = self._states[-1]

    def update(self, event: Event | None, actor: Any) -> bool:
        """Evaluate events, transition states, and execute active state logic.

        Parameters
        ----------
        event : Event | None
            Triggering event, if any.
        actor : Any
            Entity updated by current state handler.

        Returns
        -------
        bool
            False if terminal destroyed state reached; otherwise True.
        """
        if event is not None and event in self._transitions:
            for trans in self._transitions[event]:
                if isinstance(self.current, trans.from_state):
                    self.current = trans.to_state()
                    break

        self.current.update(actor)
        return not isinstance(self.current, self.end_type)


# Standard default state collection
STATES: list[type[State]] = [Idle, Moving, Firing, Reloading, Destroyed]

# Standard default transition table
TRANSITIONS: dict[Event, list[Transition]] = {
    Event.IDLE: [Transition(Reloading, Idle)],
    Event.MOVING: [Transition(Idle, Moving)],
    Event.FIRING: [Transition(Moving, Firing)],
    Event.RELOADING: [Transition(Firing, Reloading)],
    Event.DESTROYED: [Transition(Idle, Destroyed)],
}
