from src.tank import Tank


def test_tank_init():
    tank = Tank((0, 0), controls=1)
    assert tank.pos == (0, 0)
    assert tank.health == 100
    assert tank.bullet_power == 50
    assert tank.bulletHit is False


def test_tank_damage():
    tank = Tank((0, 0))
    tank.set_center_pos((0, 0))
    tank.calculate_damage((0, 0))
    assert tank.health < 100
