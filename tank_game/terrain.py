"""Terrain surface parameters and physical boundaries."""


class Terrain:
    """Represents the ground terrain layer where tanks navigate.

    Parameters
    ----------
    width : int
        Width of the game window.
    height : int
        Height of the game window.
    scale : int
        Scaling factor for display resolution.
    color : tuple[int, int, int]
        RGB tuple representing terrain color.
    ypos : int
        Vertical position where terrain surface begins.
    """

    def __init__(
        self,
        width: int,
        height: int,
        scale: int,
        color: tuple[int, int, int],
        ypos: int,
    ) -> None:
        self.friction: float = 1.0
        self.width: int = width * scale
        self.height: int = height * scale - ypos
        self.color: tuple[int, int, int] = color
        self.ypos: int = ypos
