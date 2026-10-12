"""Unit tests for tank entity logic, controls, damage, and cloning."""

import math

from tank_game.tank import Tank, TankSpawner


def test_tank_init():
    tank = Tank((50, 60), controls=1)
    assert tank.pos == (50, 60)
    assert tank.health == 100.0
    assert tank.max_health == 100
    assert tank.controls == 1
    assert tank.name == "Tank 1"
    assert tank.bulletHit is False


def test_tank_movement():
    tank = Tank((100, 100), controls=1)
    tank.set_center_pos((110, 110))
    tank.move((5, -2))
    assert tank.pos == (105, 98)
    assert tank.bullet.pos == (110.0, 110.0)


def test_tank_aim_and_power_clamping():
    tank = Tank((0, 0))
    tank.set_angle(1.0)
    assert tank.bullet_angle == 0.0  # Clamped to max 0.0

    tank.set_angle(-4.0)
    assert tank.bullet_angle == -math.pi  # Clamped to min -pi

    tank.set_power(200.0)
    assert tank.bullet_power == 100.0  # Clamped to max 100.0

    tank.set_power(-300.0)
    assert tank.bullet_power == 0.0  # Clamped to min 0.0


def test_tank_damage_calculation():
    tank = Tank((100, 100))
    tank.set_center_pos((100, 100))

    # Far away (> 50 units) = 0 damage
    dmg_far = tank.calculate_damage((200, 200))
    assert dmg_far == 0.0
    assert tank.health == 100.0

    # Direct hit (<= 1 unit) = 40 damage
    dmg_direct = tank.calculate_damage((100, 100))
    assert dmg_direct == 40.0
    assert tank.health == 60.0

    # Near hit
    dmg_near = tank.calculate_damage((105, 100))
    assert dmg_near > 0.0
    assert tank.health < 60.0


def test_tank_clone_and_spawner():
    proto = Tank((20, 30), controls=2)
    clone = TankSpawner.spawn_tank(proto)
    assert clone.pos == (20, 30)
    assert clone.controls == 2
    assert clone is not proto
