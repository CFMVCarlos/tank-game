class Terrain:
    def __init__(self, WIDTH, HEIGHT, SCALE, color, ypos) -> None:
        # Friction coefficient for terrain
        self.friction = 1
        # Width of terrain in pixels
        self.width = WIDTH * SCALE
        # Height of terrain in pixels
        self.height = HEIGHT * SCALE - ypos
        # Color of terrain
        self.color = color
        # Vertical position of terrain
        self.ypos = ypos
