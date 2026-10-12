"""Tank Game launcher entrypoint."""

import contextlib

import pygame

from tank_game.game import main


def run_launcher() -> None:
    """Initialize Pygame subsystems and start the Tank Game loop."""
    pygame.init()
    if pygame.mixer.get_init() is None:
        with contextlib.suppress(pygame.error):
            pygame.mixer.init()

    try:
        main(width=64, height=48, scale=10, username="Tank 1", lan_game=False)
    finally:
        pygame.quit()


if __name__ == "__main__":
    run_launcher()
