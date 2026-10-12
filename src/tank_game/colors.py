"""Color palette definitions for rendering game elements and HUD."""

from typing import Final

# Primary Colors
BLACK: Final[tuple[int, int, int]] = (0, 0, 0)
WHITE: Final[tuple[int, int, int]] = (255, 255, 255)
RED: Final[tuple[int, int, int]] = (255, 0, 0)
GREEN: Final[tuple[int, int, int]] = (0, 255, 0)
BLUE: Final[tuple[int, int, int]] = (0, 0, 255)

# Atmospheric & HUD Colors
SKY_BLUE: Final[tuple[int, int, int]] = (135, 206, 235)
DARK_GRAY: Final[tuple[int, int, int]] = (40, 40, 40)
LIGHT_GRAY: Final[tuple[int, int, int]] = (200, 200, 200)
GOLD: Final[tuple[int, int, int]] = (255, 215, 0)
ORANGE: Final[tuple[int, int, int]] = (255, 140, 0)
HEALTH_GREEN: Final[tuple[int, int, int]] = (46, 204, 113)
HEALTH_RED: Final[tuple[int, int, int]] = (231, 76, 60)
AIM_TRAJECTORY: Final[tuple[int, int, int]] = (255, 230, 100)
HUD_PANEL_BG: Final[tuple[int, int, int]] = (20, 20, 25)
