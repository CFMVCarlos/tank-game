from enum import Enum

# Base class for different states that a tank can be in


class State:
    def __init__(self, name: str) -> None:
        # Set the name of the state
        self.name = name

    @classmethod
    def update(cls, tank) -> None:
        # Update the state of the tank
        pass


# Class representing a transition between two states in the FSM


class Transition:
    def __init__(self, _from: State, _to: State) -> None:
        # State to transition from
        self._from = _from
        # State to transition to
        self._to = _to


# Enum representing the different events that can occur in the game


class Event(Enum):
    # Tank is idle
    IDLE = (1,)
    # Tank is moving
    MOVING = (2,)
    # Tank is firing its bullet
    FIRING = (3,)
    # Tank is reloading its bullet
    RELOADING = 4
    # Tank is destroyed
    DESTROYED = 5


# Class representing a finite state machine


class FSM:
    def __init__(
        self,
        states: list[State],
        transitions: dict[Event, list[Transition]],
    ) -> None:
        # List of possible states
        self._states = states
        # Dictionary of possible transitions between states, with the key being the event that triggers the transition
        # and the value being a list of Transition objects representing the transitions that can occur from that event
        self._transitions = transitions

        # Current state of the FSM
        self.current: State = self._states[0]
        # Final state of the FSM
        self.end: State = self._states[-1]

    def update(self, event, object) -> bool:
        # If an event was triggered, check if it causes a transition to a new state
        if event:
            for trans in self._transitions.get(event):
                if trans._from == self.current:
                    self.current = trans._to
        # Update the current state
        self.current.update(object)

        # Return False if the FSM has reached the end state, otherwise return True
        return self.current != self.end


# State representing when the tank is idle
class Idle(State):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, tank) -> None:
        # Reset the bullet position to be inside tank
        tank.bullet.set_pos(tank.center_pos)
        # Reset bulletHit to indicate bullet is stopped
        tank.bulletHit = False
        # Reset bullet.shooting indicating it is not on air
        tank.bullet.shooting = False
        # Set the current_player flag to False
        tank.current_player = False


# State representing when the tank is moving
class Moving(State):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, tank) -> None:
        # Update the position of the tank based on the commands in the commands dictionary
        for key, value in tank.commands.items():
            if key in tank.get_controls():
                value().execute(tank)


# State representing when the tank is firing its bullet
class Firing(State):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, tank) -> None:
        # Call the shoot method of the tank object
        tank.shoot()


# State representing when the tank is reloading its bullet
class Reloading(State):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, tank) -> None:
        # Update the position of the bullet
        tank.bullet.update()


# State representing when the tank is destroyed
class Destroyed(State):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, tank) -> None:
        # Do nothing
        pass


# List of possible states
STATES: list[State] = [Idle, Moving, Firing, Reloading, Destroyed]

# Dictionary of possible transitions between states, with the key being the event that triggers the transition
# and the value being a list of Transition objects representing the transitions that can occur from that event
TRANSITIONS: dict[Event, list[Transition]] = {
    # When the IDLE event is triggered, the tank can transition from the RELOADING state to the IDLE state
    Event.IDLE: [Transition(Reloading, Idle)],
    # When the MOVING event is triggered, the tank can transition from the IDLE state to the MOVING state
    Event.MOVING: [Transition(Idle, Moving)],
    # When the FIRING event is triggered, the tank can transition from the MOVING state to the FIRING state
    Event.FIRING: [Transition(Moving, Firing)],
    # When the RELOADING event is triggered, the tank can transition from the FIRING state to the RELOADING state
    Event.RELOADING: [Transition(Firing, Reloading)],
    # When the DESTROYED event is triggered, the tank can transition from the IDLE state to the DESTROYED state
    Event.DESTROYED: [Transition(Idle, Destroyed)],
}
