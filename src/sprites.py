# Standard library imports

import pygame

import colors

# Local imports
from .bullet import Bullet
from .tank import Tank
from .terrain import Terrain


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, SCALE) -> None:
        super().__init__()

        # Scale of the sprite
        self.scale: int = SCALE
        # Create a surface to draw on
        self.image: pygame.Surface = pygame.Surface([self.scale, self.scale])
        # Set the colorkey for the surface, which will be transparent when drawn
        self.image.set_colorkey("white")
        # Create a rect based on the surface
        self.rect: pygame.Rect = self.image.get_rect()


class BulletSprite(BaseSprite):
    def __init__(self, bullet: Bullet, SCALE) -> None:
        super().__init__(SCALE)

        # The bullet object associated with this sprite
        self.bullet: Bullet = bullet
        # Load the image for the bullet
        self.image: pygame.Surface = pygame.image.load("images/bullet.png").convert()
        self.image = pygame.transform.scale(
            self.image,
            (2 * (SCALE // 2), (SCALE // 2)),
        )
        # Set the colorkey for the image, which will be transparent when drawn
        self.image.set_colorkey(self.image.get_at((0, 0)))
        # Create a rect based on the image
        self.rect: pygame.Rect = self.image.get_rect()
        # Set the top left position of the rect to the position of the bullet
        self.rect.topleft: tuple[int, int] = self.bullet.pos

    def update(self) -> None:
        # Update the rect position to the position of the bullet
        self.rect.topleft = self.bullet.pos


class TankSprite(BaseSprite):
    def __init__(self, tank: Tank, SCALE) -> None:
        """Initialize TankSprite object."""
        # Call superclass initialization method
        super().__init__(SCALE)

        # Set attribute "tank" to the passed Tank object
        self.tank: Tank = tank
        # Load image for sprite and set its colorkey to the color of the top left pixel
        self.image: pygame.Surface = pygame.image.load(
            "images/tank.png",
        ).convert_alpha()
        self.image.set_colorkey(self.image.get_at((0, 0)))
        # Get a rectangular area that encloses the sprite image
        self.rect: pygame.Rect = self.image.get_rect()
        # Set the top left corner of the rectangular area to the position of the Tank object
        self.rect.topleft: tuple[int, int] = self.tank.pos
        # Define health bar size to draw
        self.health_bar_size: tuple[int, int] = (40, 4)
        # Define tank's name font
        self.font = pygame.font.Font(None, int(1.5 * self.scale))
        # Rendered text of tank's name
        self.text_name = self.font.render(f"{self.tank.name}", True, colors.BLACK)

    def update_center_pos(self) -> None:
        # Set the top left corner of the rectangular area to the position of the Tank object
        self.rect.topleft: tuple[int, int] = self.tank.pos
        # Set the center position of the Tank object to the center of the rectangular area
        self.tank.set_center_pos(self.rect.center)
        # Set the position of the bullet in the Tank object to the center position of the Tank object
        self.tank.bullet.set_pos(self.tank.center_pos)

    def draw_name(self, screen: pygame.Surface) -> None:
        # Rendered text of tank's name
        self.text_name = self.font.render(f"{self.tank.name}", True, colors.BLACK)
        # Get the dimensions of the rendered text
        text_rect = self.text_name.get_rect()
        # Set the position of the text so it is centered on the screen
        text_rect.center = (
            self.rect.centerx,
            self.rect.top - self.health_bar_size[1] - text_rect.height / 2,
        )
        screen.blit(self.text_name, text_rect)

    def draw_health(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen,
            colors.RED,
            pygame.Rect(
                self.rect.centerx,
                self.rect.top,
                (self.health_bar_size[0]) * self.tank.health / self.tank.max_health,
                2 * self.health_bar_size[1],
            ).move(-self.health_bar_size[0] / 2, -self.health_bar_size[1]),
        )
        pygame.draw.rect(
            screen,
            colors.BLACK,
            pygame.Rect(
                self.rect.centerx,
                self.rect.top,
                self.health_bar_size[0],
                2 * self.health_bar_size[1],
            ).move(-self.health_bar_size[0] / 2, -self.health_bar_size[1]),
            width=1,
        )

    def update(self) -> None:
        """Update sprite's position and Tank object's center position."""
        # Set the top left corner of the rectangular area to the position of the Tank object
        self.rect.topleft = self.tank.pos
        # Set the center position of the Tank object to the center of the rectangular area
        self.tank.set_center_pos(self.rect.center)
        if self.tank.health <= 0:
            self.image: pygame.Surface = pygame.image.load(
                "images/Tank_Explosion_4.png",
            ).convert_alpha()
        elif self.tank.health < 0.1 * self.tank.max_health:
            self.image: pygame.Surface = pygame.image.load(
                "images/Tank_Explosion_3.png",
            ).convert_alpha()
        elif self.tank.health < 0.25 * self.tank.max_health:
            self.image: pygame.Surface = pygame.image.load(
                "images/Tank_Explosion_2.png",
            ).convert_alpha()
        elif self.tank.health < 0.5 * self.tank.max_health:
            self.image: pygame.Surface = pygame.image.load(
                "images/Tank_Explosion_1.png",
            ).convert_alpha()
        elif self.tank.health < 0.75 * self.tank.max_health:
            self.image: pygame.Surface = pygame.image.load(
                "images/Tank_Explosion_0.png",
            ).convert_alpha()

    def get_bottom_pos(self) -> int:
        """Return the y-coordinate of the bottom of the sprite."""
        return self.tank.pos[1] + self.image.get_height()


class TerrainSprite(BaseSprite):
    def __init__(self, terrain: Terrain, SCALE) -> None:
        """Initialize TerrainSprite object."""
        super().__init__(SCALE)

        # Assign terrain object to sprite
        self.terrain: Terrain = terrain
        # Load terrain image for sprite
        self.image: pygame.Surface = pygame.image.load(
            "images/grass_dirt_block.png",
        ).convert()
        # Scale image to terrain dimensions
        self.image = pygame.transform.scale(self.image, (terrain.width, terrain.height))
        # Get the rect of the image and move the rect to the y position of the terrain
        self.rect: pygame.Rect = self.image.get_rect().move((0, self.terrain.ypos))
