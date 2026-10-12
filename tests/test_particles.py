"""Unit tests for the particle effects engine."""

from tank_game.particles import Particle, ParticleManager


def test_particle_lifecycle():
    p = Particle(x=10.0, y=20.0, color=(255, 200, 0), velocity=(1.0, -2.0), lifetime=3)
    assert p.alive is True
    assert p.age == 0

    p.update()
    assert p.x > 10.0
    assert p.age == 1
    assert p.alive is True

    p.update()
    p.update()
    assert p.alive is False


def test_particle_manager_burst():
    mgr = ParticleManager()
    assert len(mgr.particles) == 0

    mgr.spawn_explosion_burst((50, 60), count=20)
    assert len(mgr.particles) == 20

    mgr.spawn_spark_trail((50, 60))
    assert len(mgr.particles) == 22

    # Advance until short sparks expire
    for _ in range(12):
        mgr.update()

    assert len(mgr.particles) <= 20
