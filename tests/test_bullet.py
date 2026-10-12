"""Unit tests for bullet physics and ballistic state."""

from tank_game.bullet import Bullet


def test_bullet_initialization():
    bullet = Bullet((100, 200))
    assert bullet.pos == (100.0, 200.0)
    assert not bullet.shooting
    assert bullet.bullet_hit_position == (100, 200)


def test_bullet_shoot():
    bullet = Bullet((10, 20))
    bullet.shoot((50, 60), angle=0.0, power=80.0)
    assert bullet.pos == (50.0, 60.0)
    assert bullet.shooting is True
    assert bullet.power == 60.0  # 80 * 0.75
    assert bullet.velocity[0] == 60.0
    assert abs(bullet.velocity[1]) < 1e-5


def test_bullet_trajectory_update():
    bullet = Bullet((0, 0))
    bullet.shoot((0, 0), angle=0.0, power=40.0)
    init_x, init_y = bullet.pos
    bullet.update()
    assert bullet.pos[0] > init_x
    assert bullet.pos[1] > init_y  # Gravity pushes downwards (+y in Pygame)


def test_bullet_set_pos_and_hit():
    bullet = Bullet((0, 0))
    bullet.set_pos((30, 40))
    assert bullet.pos == (30.0, 40.0)

    bullet.set_bullet_hit_position((75, 85))
    assert bullet.bullet_hit_position == (75, 85)
