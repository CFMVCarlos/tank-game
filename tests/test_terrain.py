from src.terrain import Terrain


def test_terrain_init():
    terrain = Terrain(800, 600, 1, (0, 255, 0), 500)
    assert terrain.width == 800
    assert terrain.height == 100
    assert terrain.color == (0, 255, 0)
    assert terrain.ypos == 500
