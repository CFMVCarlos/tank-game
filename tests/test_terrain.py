"""Unit tests for terrain surface properties."""

from tank_game.terrain import Terrain


def test_terrain_init():
    terrain = Terrain(width=64, height=48, scale=10, color=(0, 255, 0), ypos=400)
    assert terrain.width == 640
    assert terrain.height == 80  # 480 - 400
    assert terrain.ypos == 400
    assert terrain.color == (0, 255, 0)
    assert terrain.friction == 1.0
