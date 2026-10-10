from src.bullet import Bullet


def test_bullet_init():
    bullet = Bullet((10, 10))
    assert bullet.pos == (10, 10)
    assert not bullet.shooting


def test_bullet_shoot():
    bullet = Bullet((10, 10))
    bullet.shoot((20, 20), 0, 100)
    assert bullet.pos == (20, 20)
    assert bullet.shooting
    assert bullet.power == 75
    assert bullet.velocity == (75, 0)


def test_bullet_update():
    bullet = Bullet((10, 10))
    bullet.shoot((10, 10), 0, 100)
    bullet.update()
    assert bullet.pos[0] > 10
