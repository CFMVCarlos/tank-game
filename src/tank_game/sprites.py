"""Pygame Sprite entities with centralized asset caching and optimized rendering."""

from pathlib import Path
from typing import ClassVar

import pygame

from tank_game import colors
from tank_game.bullet import Bullet
from tank_game.tank import Tank
from tank_game.terrain import Terrain


class AssetCache:
    """Central repository preloading and caching graphics and audio assets.

    Eliminates per-frame disk reading and surface conversion overhead.
    """

    _images: ClassVar[dict[str, pygame.Surface]] = {}
    _sounds: ClassVar[dict[str, pygame.mixer.Sound]] = {}
    _initialized: ClassVar[bool] = False

    @classmethod
    def _find_asset_path(cls, filename: str) -> Path:
        """Locate asset file path handling potential cross-platform casing differences.

        Parameters
        ----------
        filename : str
            Requested asset relative path or name.

        Returns
        -------
        Path
            Validated filesystem path to the asset.

        Raises
        ------
        FileNotFoundError
            If asset cannot be located under images/ or root.
        """
        target = Path(filename)
        if target.exists():
            return target

        img_target = Path("images") / target.name
        if img_target.exists():
            return img_target

        # Case-insensitive search under images/
        img_dir = Path("images")
        if img_dir.exists():
            lower_name = target.name.lower()
            for child in img_dir.iterdir():
                if child.name.lower() == lower_name:
                    return child

        msg = f"Asset not found: {filename}"
        raise FileNotFoundError(msg)

    @classmethod
    def get_image(cls, filename: str, alpha: bool = True) -> pygame.Surface:
        """Retrieve preloaded image surface from cache or load once.

        Parameters
        ----------
        filename : str
            Path or basename of the image asset.
        alpha : bool, default=True
            Whether to convert with per-pixel alpha transparency.

        Returns
        -------
        pygame.Surface
            Cached display surface ready for blitting.
        """
        if filename not in cls._images:
            path = cls._find_asset_path(filename)
            raw = pygame.image.load(str(path))
            surface = raw.convert_alpha() if alpha else raw.convert()
            cls._images[filename] = surface
        return cls._images[filename]

    @classmethod
    def get_sound(cls, filename: str) -> pygame.mixer.Sound | None:
        """Retrieve preloaded sound effect or load once safely.

        Parameters
        ----------
        filename : str
            Path or basename of the audio asset.

        Returns
        -------
        pygame.mixer.Sound | None
            Cached sound instance, or None if audio subsystem is unavailable.
        """
        if pygame.mixer.get_init() is None:
            return None
        if filename not in cls._sounds:
            try:
                path = cls._find_asset_path(filename)
                cls._sounds[filename] = pygame.mixer.Sound(str(path))
            except (pygame.error, FileNotFoundError):
                return None
        return cls._sounds.get(filename)


class BaseSprite(pygame.sprite.Sprite):
    """Base class for scaling and positioning game visual sprites.

    Parameters
    ----------
    scale : int
        Screen coordinate scaling factor.
    """

    def __init__(self, scale: int) -> None:
        super().__init__()
        self.scale: int = scale


class BulletSprite(BaseSprite):
    """Visual sprite representing a moving artillery bullet in flight.

    Parameters
    ----------
    bullet : Bullet
        Associated physics model.
    scale : int
        Scaling factor.
    """

    def __init__(self, bullet: Bullet, scale: int) -> None:
        super().__init__(scale)
        self.bullet: Bullet = bullet
        raw_img = AssetCache.get_image("bullet.png", alpha=False)
        w = max(4, 2 * (scale // 2))
        h = max(2, scale // 2)
        self.image: pygame.Surface = pygame.transform.scale(raw_img, (w, h))
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect: pygame.Rect = self.image.get_rect()

    def update(self) -> None:
        """Synchronize sprite rect location with underlying bullet coordinates."""
        self.rect.topleft = (
            int(self.bullet.pos[0]),
            int(self.bullet.pos[1]),
        )


class TankSprite(BaseSprite):
    """Visual sprite rendering tank body, name tag, health bar, and damage states.

    Parameters
    ----------
    tank : Tank
        Associated combat tank model.
    scale : int
        Scaling factor.
    """

    def __init__(self, tank: Tank, scale: int) -> None:
        super().__init__(scale)
        self.tank: Tank = tank
        self.base_image: pygame.Surface = AssetCache.get_image("Tank.png")
        self.image: pygame.Surface = self.base_image
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = tank.pos

        # Pre-cache explosion damage surfaces
        self.explosion_stages: list[pygame.Surface] = [
            AssetCache.get_image(f"Tank_Explosion_{i}.png") for i in range(5)
        ]

        # UI & HUD geometry
        self.font: pygame.font.Font = pygame.font.SysFont("Verdana", max(11, 14))
        self.health_bar_size: tuple[int, int] = (int(self.rect.width * 1.2), 6)

        self.update_center_pos()

    def update_center_pos(self) -> None:
        """Update center coordinates of the tank and synchronize bullet origin."""
        self.tank.set_center_pos(self.rect.center)
        self.tank.bullet.set_pos(self.tank.center_pos)

    def draw_name(self, screen: pygame.Surface) -> None:
        """Render player identification badge above the tank.

        Parameters
        ----------
        screen : pygame.Surface
            Target display canvas.
        """
        text_name = self.font.render(self.tank.name, True, colors.DARK_GRAY)
        text_rect = text_name.get_rect()
        text_rect.center = (
            self.rect.centerx,
            int(self.rect.top - self.health_bar_size[1] - text_rect.height / 2 - 4),
        )
        screen.blit(text_name, text_rect)

    def draw_health(self, screen: pygame.Surface) -> None:
        """Render arcade health bar with background panel, health fill, and border.

        Parameters
        ----------
        screen : pygame.Surface
            Target display canvas.
        """
        bar_w, bar_h = self.health_bar_size
        bar_x = int(self.rect.centerx - bar_w / 2)
        bar_y = int(self.rect.top - bar_h - 2)

        # Background container
        bg_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(screen, colors.DARK_GRAY, bg_rect, border_radius=2)

        # Filled health portion
        health_ratio = max(0.0, min(1.0, self.tank.health / self.tank.max_health))
        fill_w = int(bar_w * health_ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
            fill_color = (
                colors.HEALTH_GREEN if health_ratio > 0.4 else colors.HEALTH_RED
            )
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=2)

        # Border outline
        pygame.draw.rect(screen, colors.BLACK, bg_rect, width=1, border_radius=2)

    def update(self) -> None:
        """Update sprite position, center geometry, and select damage frame."""
        self.rect.topleft = self.tank.pos
        self.tank.set_center_pos(self.rect.center)

        # In-memory stage selection without disk I/O
        health_ratio = self.tank.health / self.tank.max_health
        if self.tank.health <= 0:
            self.image = self.explosion_stages[4]
        elif health_ratio < 0.10:
            self.image = self.explosion_stages[3]
        elif health_ratio < 0.25:
            self.image = self.explosion_stages[2]
        elif health_ratio < 0.50:
            self.image = self.explosion_stages[1]
        elif health_ratio < 0.75:
            self.image = self.explosion_stages[0]
        else:
            self.image = self.base_image

    def get_bottom_pos(self) -> int:
        """Return the vertical y-coordinate of the bottom of the sprite.

        Returns
        -------
        int
            Bottom coordinate y value.
        """
        return int(self.tank.pos[1] + self.image.get_height())


class TerrainSprite(BaseSprite):
    """Visual ground layer sprite scaled across the width of the battlefield.

    Parameters
    ----------
    terrain : Terrain
        Underlying terrain model.
    scale : int
        Scaling factor.
    """

    def __init__(self, terrain: Terrain, scale: int) -> None:
        super().__init__(scale)
        self.terrain: Terrain = terrain
        raw_img = AssetCache.get_image("grass_dirt_block.png", alpha=False)
        self.image: pygame.Surface = pygame.transform.scale(
            raw_img,
            (terrain.width, terrain.height),
        )
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = (0, terrain.ypos)
