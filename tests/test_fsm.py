"""Unit tests for the FSM engine and state transitions."""

from tank_game.fsm import (
    FSM,
    STATES,
    TRANSITIONS,
    Destroyed,
    Event,
    Firing,
    Idle,
    Moving,
    Reloading,
)
from tank_game.tank import Tank


def test_fsm_initial_state():
    fsm = FSM(STATES, TRANSITIONS)
    assert isinstance(fsm.current, Idle)


def test_fsm_transition_sequence():
    fsm = FSM(STATES, TRANSITIONS)
    tank = Tank((0, 0))

    # Idle -> Moving
    active = fsm.update(Event.MOVING, tank)
    assert active is True
    assert isinstance(fsm.current, Moving)

    # Moving -> Firing
    active = fsm.update(Event.FIRING, tank)
    assert active is True
    assert isinstance(fsm.current, Firing)

    # Firing -> Reloading
    active = fsm.update(Event.RELOADING, tank)
    assert active is True
    assert isinstance(fsm.current, Reloading)

    # Reloading -> Idle
    active = fsm.update(Event.IDLE, tank)
    assert active is True
    assert isinstance(fsm.current, Idle)


def test_fsm_terminal_destroyed_state():
    fsm = FSM(STATES, TRANSITIONS)
    tank = Tank((0, 0))

    # Idle -> Destroyed
    active = fsm.update(Event.DESTROYED, tank)
    assert active is False
    assert isinstance(fsm.current, Destroyed)
