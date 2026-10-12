"""Tank Game launcher entrypoint."""

import contextlib
import sys

import pygame

from tank_game.game import main


def run_launcher() -> None:
    """Initialize Pygame subsystems and start the Tank Game loop."""
    pygame.init()
    if pygame.mixer.get_init() is None:
        with contextlib.suppress(pygame.error):
            pygame.mixer.init()

    username = "Tank 1"
    lan_mode = False

    if sys.stdin.isatty():
        try:
            raw_name = input("Insert your name (default: Tank 1): ").strip()
            if raw_name:
                username = raw_name
            raw_lan = input(
                "Local or LAN game? (0 for Local, 1 for LAN, default 0): "
            ).strip()
            lan_mode = raw_lan == "1"
        except (EOFError, KeyboardInterrupt):
            pass

    try:
        main(width=64, height=48, scale=10, username=username, lan_game=lan_mode)
    finally:
        pygame.quit()


if __name__ == "__main__":
    run_launcher()
