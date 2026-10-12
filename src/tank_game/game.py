"""Core game loop, input routing, collision handling, and HUD rendering."""

import math
import random
from typing import Any

import pygame

from tank_game import colors
from tank_game.network import (
    create_receiver_socket,
    create_sender_socket,
    receive_json_message,
    send_json_message,
)
from tank_game.particles import ParticleManager
from tank_game.sprites import AssetCache, BulletSprite, TankSprite, TerrainSprite
from tank_game.tank import Tank, TankSpawner
from tank_game.terrain import Terrain


def calculate_line_intersection(
    line1: tuple[float, float, float, float],
    line2: tuple[float, float, float, float],
) -> tuple[float, float] | None:
    """Calculate intersection point between two line segments if they intersect.

    Parameters
    ----------
    line1 : tuple[float, float, float, float]
        Segment coordinates (x1, y1, x2, y2).
    line2 : tuple[float, float, float, float]
        Segment coordinates (x3, y3, x4, y4).

    Returns
    -------
    tuple[float, float] | None
        Intersection coordinate (x, y) if lines cross; otherwise None.
    """
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-6:
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def is_off_screen(width: int, center_x: int) -> bool:
    """Check if horizontal position has left screen boundaries.

    Parameters
    ----------
    width : int
        Maximum screen width in pixels.
    center_x : int
        Current horizontal coordinate.

    Returns
    -------
    bool
        True if off-screen; otherwise False.
    """
    return center_x < 0 or center_x > width


def draw_aim_trajectory(
    screen: pygame.Surface,
    origin: tuple[int, int],
    power: float,
    angle: float,
    num_points: int = 16,
) -> None:
    """Draw a segmented ballistic aim arc predicting shot path.

    Parameters
    ----------
    screen : pygame.Surface
        Target Pygame canvas.
    origin : tuple[int, int]
        Turret launch origin coordinates (x, y).
    power : float
        Current shot velocity magnitude.
    angle : float
        Current turret launch angle in radians.
    num_points : int, default=16
        Number of preview trajectory dots.
    """
    scaled_power = power * 0.75
    vx = scaled_power * math.cos(angle)
    vy = scaled_power * math.sin(angle)
    gravity_y = 0.98

    curr_x, curr_y = float(origin[0]), float(origin[1])
    for step in range(1, num_points + 1):
        curr_x += vx
        curr_y += vy
        vy += gravity_y

        dot_radius = max(1, 3 - (step // 6))
        pygame.draw.circle(
            screen,
            colors.AIM_TRAJECTORY,
            (int(curr_x), int(curr_y)),
            dot_radius,
        )


def draw_hud(
    screen: pygame.Surface,
    font: pygame.font.Font,
    tank: Tank,
    current_player: int,
    screen_width: int,
) -> None:
    """Render arcade HUD panel showing active player, power, and turret angle.

    Parameters
    ----------
    screen : pygame.Surface
        Display canvas.
    font : pygame.font.Font
        Render font.
    tank : Tank
        Active player's tank instance.
    current_player : int
        Active turn index (1 or 2).
    screen_width : int
        Total screen width in pixels.
    """
    # Top turn indicator
    turn_text = f"PLAYER {current_player}'S TURN"
    turn_color = colors.GOLD if current_player == 1 else colors.SKY_BLUE
    turn_surf = font.render(turn_text, True, turn_color)
    turn_rect = turn_surf.get_rect(center=(screen_width // 2, 20))
    screen.blit(turn_surf, turn_rect)

    # Bottom status bar
    angle_deg = int(abs(math.degrees(tank.bullet_angle)))
    stats_text = f"POWER: {int(tank.bullet_power)}%   |   ANGLE: {angle_deg}°"
    stats_surf = font.render(stats_text, True, colors.WHITE)
    stats_rect = stats_surf.get_rect(center=(screen_width // 2, 45))
    screen.blit(stats_surf, stats_rect)


def show_start_screen(
    screen: pygame.Surface,
    bg_surf: pygame.Surface,
    clock: pygame.time.Clock,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    sub_font: pygame.font.Font,
    screen_w: int,
    screen_h: int,
) -> bool:
    """Render start splash menu and wait for player to start or quit.

    Parameters
    ----------
    screen : pygame.Surface
        Display canvas.
    bg_surf : pygame.Surface
        Scaled sky background image.
    clock : pygame.time.Clock
        Frame rate limiter.
    title_font : pygame.font.Font
        Main title font.
    font : pygame.font.Font
        Standard menu font.
    sub_font : pygame.font.Font
        Subheading / control list font.
    screen_w : int
        Window width in pixels.
    screen_h : int
        Window height in pixels.

    Returns
    -------
    bool
        True to begin game; False if player quits.
    """
    pulse_frame = 0
    waiting = True
    while waiting:
        pulse_frame += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                return False
            if event.type in {pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN}:
                return True

        screen.blit(bg_surf, (0, 0))

        # Semi-transparent overlay panel
        panel_w, panel_h = min(560, screen_w - 40), min(420, screen_h - 40)
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((15, 20, 30, 225))
        pygame.draw.rect(
            panel,
            colors.GOLD,
            panel.get_rect(),
            width=2,
            border_radius=12,
        )
        screen.blit(panel, ((screen_w - panel_w) // 2, (screen_h - panel_h) // 2))

        # Title banner
        title_surf = title_font.render("TANKS ARCADE", True, colors.GOLD)
        title_rect = title_surf.get_rect(center=(screen_w // 2, screen_h // 2 - 140))
        screen.blit(title_surf, title_rect)

        sub_surf = font.render("Ballistic Artillery Combat", True, colors.SKY_BLUE)
        sub_rect = sub_surf.get_rect(center=(screen_w // 2, screen_h // 2 - 100))
        screen.blit(sub_surf, sub_rect)

        # Controls reference guide
        ctrl_lines = [
            ("PLAYER 1 CONTROLS", colors.GOLD),
            ("Move: A / D    |    Aim: Q / E    |    Power: W / S", colors.WHITE),
            ("Fire: SPACE", colors.LIGHT_GRAY),
            ("", colors.WHITE),
            ("PLAYER 2 CONTROLS", colors.SKY_BLUE),
            ("Move: ← / →    |    Aim: U / O    |    Power: ↑ / ↓", colors.WHITE),
            ("Fire: ENTER", colors.LIGHT_GRAY),
        ]

        y_offset = screen_h // 2 - 50
        for text, color in ctrl_lines:
            if text:
                line_surf = sub_font.render(text, True, color)
                line_rect = line_surf.get_rect(center=(screen_w // 2, y_offset))
                screen.blit(line_surf, line_rect)
            y_offset += 24

        # Pulsing prompt
        prompt_color = colors.GOLD if (pulse_frame // 30) % 2 == 0 else colors.WHITE
        prompt_surf = font.render("PRESS ANY KEY OR CLICK TO START", True, prompt_color)
        prompt_rect = prompt_surf.get_rect(center=(screen_w // 2, screen_h // 2 + 155))
        screen.blit(prompt_surf, prompt_rect)

        pygame.display.flip()
        clock.tick(60)

    return True


def run_game(
    width: int = 64,
    height: int = 48,
    scale: int = 10,
    username: str = "Tank 1",
    lan_game: bool = False,
    max_frames: int | None = None,
    show_menu: bool = True,
) -> bool:
    """Execute the core tank battle game loop.

    Parameters
    ----------
    width : int, default=64
        Virtual width unit count.
    height : int, default=48
        Virtual height unit count.
    scale : int, default=10
        Screen scaling multiplier.
    username : str, default="Tank 1"
        Local player display name.
    lan_game : bool, default=False
        Enable UDP multicast LAN synchronization.
    max_frames : int | None, default=None
        Optional maximum frame limit for headless/test executions.
    show_menu : bool, default=True
        Display interactive title start screen before combat.

    Returns
    -------
    bool
        True upon normal game exit.
    """
    screen_w = width * scale
    screen_h = height * scale
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Tanks Game - Arcade Edition")

    # Background loading with fallback scaling
    bg_raw = AssetCache.get_image("sky_background.png", alpha=False)
    bg_surf = pygame.transform.scale(bg_raw, (screen_w, screen_h))

    clock = pygame.time.Clock()
    particles = ParticleManager()
    title_font = pygame.font.SysFont("Verdana", max(22, 26 * scale // 10), bold=True)
    font = pygame.font.SysFont("Verdana", max(12, 14 * scale // 10), bold=True)
    sub_font = pygame.font.SysFont("Verdana", max(10, 11 * scale // 10))
    hud_font = pygame.font.SysFont("Verdana", max(10, 11 * scale // 10), bold=True)

    # Show start screen if enabled (disabled in headless automated tests)
    if (
        show_menu
        and max_frames is None
        and not show_start_screen(
            screen=screen,
            bg_surf=bg_surf,
            clock=clock,
            title_font=title_font,
            font=font,
            sub_font=sub_font,
            screen_w=screen_w,
            screen_h=screen_h,
        )
    ):
        return True

    # Spawning tanks
    tank_base = Tank((-10, -10), controls=1)
    tank1 = TankSpawner.spawn_tank(tank_base)
    tank2 = TankSpawner.spawn_tank(tank_base)

    tank1.set_pos((screen_w // 4, 3 * screen_h // 4))
    tank1.set_controls(1).set_tank_name(username)
    tank2.set_pos((3 * screen_w // 4, 3 * screen_h // 4))
    tank2.set_controls(2).set_tank_name("Tank 2")

    tank1_sprite = TankSprite(tank1, scale)
    tank2_sprite = TankSprite(tank2, scale)

    terrain = Terrain(width, height, scale, colors.GREEN, tank1_sprite.get_bottom_pos())
    terrain_sprite = TerrainSprite(terrain, scale)

    bullet1_sprite = BulletSprite(tank1.bullet, scale)
    bullet2_sprite = BulletSprite(tank2.bullet, scale)

    all_sprites = pygame.sprite.Group(
        terrain_sprite,  # pyright: ignore[reportArgumentType]
        tank1_sprite,  # pyright: ignore[reportArgumentType]
        tank2_sprite,  # pyright: ignore[reportArgumentType]
        bullet1_sprite,  # pyright: ignore[reportArgumentType]
        bullet2_sprite,  # pyright: ignore[reportArgumentType]
    )

    # Network configuration
    sender_sock = create_sender_socket() if lan_game else None
    receiver_sock = create_receiver_socket() if lan_game else None
    user_id = random.randint(1000, 999999)

    current_player: int = 1
    tank1.current_player = True
    game_over: bool = False
    game_winner: int = 0
    frame_count: int = 0

    running: bool = True
    while running:
        frame_count += 1
        if max_frames is not None and frame_count >= max_frames:
            break

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        if not running:
            break

        # Key state handling
        keys_pressed = pygame.key.get_pressed()
        remote_keys: dict[int, bool] = {}

        if lan_game and receiver_sock and sender_sock:
            # Poll for incoming network state packets
            msg = receive_json_message(receiver_sock)
            if msg and msg.get("user_id") != user_id:
                incoming_keys = msg.get("keys", [])
                remote_keys = {int(k): True for k in incoming_keys}

            active_keys = [k for k, v in enumerate(keys_pressed) if v]
            if active_keys:
                send_json_message(
                    sender_sock,
                    {"user": username, "user_id": user_id, "keys": active_keys},
                )

        # Merge local keyboard state and remote network events
        if remote_keys:
            key_source = dict.fromkeys(remote_keys, True)
            for k, val in enumerate(keys_pressed):
                if val:
                    key_source[k] = True
        else:
            key_source = keys_pressed

        # Update entities
        tank1.update(key_source)
        tank2.update(key_source)

        # Bullet spark trails during active flight
        if tank1.bullet.shooting:
            particles.spawn_spark_trail(bullet1_sprite.rect.center)
        if tank2.bullet.shooting:
            particles.spawn_spark_trail(bullet2_sprite.rect.center)

        # Terrain / Tank collision detection for bullet 1
        if tank1.bullet.shooting:
            bullet_box = (
                bullet1_sprite.rect.left,
                bullet1_sprite.rect.top,
                bullet1_sprite.rect.right,
                bullet1_sprite.rect.bottom,
            )
            ground_box = (
                0.0,
                float(terrain.ypos),
                float(screen_w),
                float(terrain.ypos),
            )
            impact = calculate_line_intersection(bullet_box, ground_box)

            off_screen = is_off_screen(screen_w, bullet1_sprite.rect.centerx)
            ground_hit = bullet1_sprite.rect.bottom >= terrain.ypos
            if impact or off_screen or ground_hit:
                hit_pos = (
                    int(impact[0]) if impact else bullet1_sprite.rect.centerx,
                    int(impact[1]) if impact else terrain.ypos,
                )
                tank1.bullet.set_bullet_hit_position(hit_pos)
                tank1.bulletHit = True
                particles.spawn_explosion_burst(hit_pos, count=35)
                snd = AssetCache.get_sound("Explosion.wav")
                if snd:
                    snd.play()

                # Calculate damage on opponent
                tank2.calculate_damage(hit_pos)
                tank1.current_player = False
                tank2.current_player = True
                current_player = 2

        # Terrain / Tank collision detection for bullet 2
        if tank2.bullet.shooting:
            bullet_box = (
                bullet2_sprite.rect.left,
                bullet2_sprite.rect.top,
                bullet2_sprite.rect.right,
                bullet2_sprite.rect.bottom,
            )
            ground_box = (
                0.0,
                float(terrain.ypos),
                float(screen_w),
                float(terrain.ypos),
            )
            impact = calculate_line_intersection(bullet_box, ground_box)

            off_screen = is_off_screen(screen_w, bullet2_sprite.rect.centerx)
            ground_hit = bullet2_sprite.rect.bottom >= terrain.ypos
            if impact or off_screen or ground_hit:
                hit_pos = (
                    int(impact[0]) if impact else bullet2_sprite.rect.centerx,
                    int(impact[1]) if impact else terrain.ypos,
                )
                tank2.bullet.set_bullet_hit_position(hit_pos)
                tank2.bulletHit = True
                particles.spawn_explosion_burst(hit_pos, count=35)
                snd = AssetCache.get_sound("Explosion.wav")
                if snd:
                    snd.play()

                # Calculate damage on opponent
                tank1.calculate_damage(hit_pos)
                tank2.current_player = False
                tank1.current_player = True
                current_player = 1

        # Check win/loss state
        if tank1.health <= 0 and not game_over:
            game_over = True
            game_winner = 2
        elif tank2.health <= 0 and not game_over:
            game_over = True
            game_winner = 1

        # Update sprite positions
        all_sprites.update()
        particles.update()

        # Rendering pipeline
        screen.blit(bg_surf, (0, 0))
        all_sprites.draw(screen)

        # Draw HUD nameplates and health bars
        tank1_sprite.draw_name(screen)
        tank1_sprite.draw_health(screen)
        tank2_sprite.draw_name(screen)
        tank2_sprite.draw_health(screen)

        # Draw aim trajectory arc for active player
        if not game_over:
            active_tank = tank1 if current_player == 1 else tank2
            if not active_tank.bullet.shooting:
                active_sprite = tank1_sprite if current_player == 1 else tank2_sprite
                draw_aim_trajectory(
                    screen,
                    active_sprite.rect.center,
                    active_tank.bullet_power,
                    active_tank.bullet_angle,
                )
            draw_hud(screen, hud_font, active_tank, current_player, screen_w)

        # Draw dynamic particle effects
        particles.draw(screen)

        # Render victory announcement
        if game_over:
            winner_name = tank1.name if game_winner == 1 else tank2.name
            banner = font.render(f"VICTORY! {winner_name} WON!", True, colors.GOLD)
            banner_rect = banner.get_rect(center=(screen_w // 2, screen_h // 3))
            banner_bg = banner_rect.inflate(30, 20)
            pygame.draw.rect(screen, colors.HUD_PANEL_BG, banner_bg, border_radius=6)
            pygame.draw.rect(screen, colors.GOLD, banner_bg, width=2, border_radius=6)
            screen.blit(banner, banner_rect)

        pygame.display.flip()
        clock.tick(60)

    if sender_sock:
        sender_sock.close()
    if receiver_sock:
        receiver_sock.close()

    return True


# Backward-compatible entrypoint
def main(
    width: int = 64,
    height: int = 48,
    scale: int = 10,
    **kwargs: Any,
) -> bool:
    """Launch main game with default configurations.

    Parameters
    ----------
    width : int, default=64
        Virtual width units.
    height : int, default=48
        Virtual height units.
    scale : int, default=10
        Resolution scale factor.
    **kwargs : Any
        Additional keyword arguments forwarded to run_game.

    Returns
    -------
    bool
        True upon exit.
    """
    return run_game(width=width, height=height, scale=scale, **kwargs)
