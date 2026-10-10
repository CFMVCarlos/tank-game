# Standard library imports
import math
import pickle
import random
import sys

import pygame

import colors
from .multicast_transceiver import createReceiverSocket, createSenderSocket, sendMessage
from .sprites import BulletSprite, TankSprite, TerrainSprite

# Local imports
from .tank import Tank, Tank_Spawner
from .terrain import Terrain

FRAMES: int = 0
FRAME_LIMIT: int = 60
SOUND_PLAYED_ONCE: bool = True


def intersection(line1, line2):
    """Calculate the intersection point between two lines. Each line is represented
    by a tuple of four elements (x1, y1, x2, y2) that correspond to the coordinates
    of the two points that define the line. The function returns a tuple with the
    coordinates of the intersection point if the lines intersect, or None if the
    lines are parallel or don't intersect.
    """
    # Extract the points from the lines
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    # Calculate the intersection point
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # Lines are parallel
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        # Calculate the intersection point
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)
    return None  # Lines do not intersect


def check_off_limits(gameWidth: int, rect_centerx: int) -> bool:
    # Check if the center x position of the given rectangle is outside of the game screen
    return rect_centerx > gameWidth or rect_centerx < 0


def bullet_hit_animation(
    start_animation: bool,
    screen: pygame.Surface,
    sound: pygame.mixer.Sound,
    image: pygame.Surface,
    position: tuple[int, int],
) -> bool:
    """Plays bullet hit animation and sound."""
    global FRAMES, FRAME_LIMIT, SOUND_PLAYED_ONCE
    if not start_animation:
        return False

    if SOUND_PLAYED_ONCE:
        # Play explosion sound once per animation
        sound.play()
        # Reset flag to only play sound once per explosion
        SOUND_PLAYED_ONCE = False
    # Draw explosion image on the screen
    screen.blit(image, position)
    # Increase frames
    FRAMES += 1
    # If total of frames per animation reaches FRAME_LIMIT, corresponds to 1 second
    if FRAMES == FRAME_LIMIT:
        # Reset sound played flag and frames counter
        SOUND_PLAYED_ONCE = True
        FRAMES = 0
        return True
    return False


def main(WIDTH: int, HEIGHT: int, SCALE: int) -> bool:
    # Create the window
    screen: pygame.Surface = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
    # Set the title of the window
    pygame.display.set_caption("Tanks Game")
    # Load background image
    background_image: pygame.Surface = pygame.image.load("images/sky_background.png")
    background_image_offset = random.randint(
        0,
        background_image.get_size()[0] - WIDTH * SCALE,
    )
    background_image = pygame.transform.scale(
        background_image,
        (background_image.get_width(), HEIGHT * (SCALE + 1)),
    )
    # Set the key repeat delay and interval
    pygame.key.set_repeat(50, 50)
    # Load explosion sound
    explosion_sound: pygame.mixer.Sound = pygame.mixer.Sound("images/explosion.wav")
    # Load explosion image
    explosion_image: pygame.Surface = pygame.image.load(
        "images/explosion.png",
    ).convert_alpha()
    explosion_image = pygame.transform.scale(explosion_image, (2 * SCALE, 2 * SCALE))
    # Create a Pygame clock to control the frame rate
    clock: pygame.time.Clock = pygame.time.Clock()

    # Create players tank
    TankSpawner = Tank_Spawner()
    tank_base = Tank((-10, -10), controls=1)
    tank1_sprite: TankSprite = TankSprite(TankSpawner.spawn_tank(tank_base), SCALE)
    tank2_sprite: TankSprite = TankSprite(TankSpawner.spawn_tank(tank_base), SCALE)
    tank1_sprite.tank.set_pos((WIDTH * SCALE / 4, 3 * HEIGHT * SCALE / 4)).set_controls(
        1,
    ).set_tank_name(USERNAME)
    tank2_sprite.tank.set_pos(
        (
            3 * WIDTH * SCALE / 4,
            3 * HEIGHT * SCALE / 4,
        )
    ).set_controls(2).set_tank_name("Tank 2")
    tank1_sprite.update_center_pos()
    tank2_sprite.update_center_pos()
    # Create terrain for tanks to move
    terrain_sprite = TerrainSprite(
        Terrain(WIDTH, HEIGHT, SCALE, colors.GREEN, tank1_sprite.get_bottom_pos()),
        SCALE,
    )
    # Create bullet sprites for tanks
    bullet1_sprite: BulletSprite = BulletSprite(tank1_sprite.tank.bullet, SCALE)
    bullet2_sprite: BulletSprite = BulletSprite(tank2_sprite.tank.bullet, SCALE)
    # Add all sprites to a group of sprites
    all_sprites = pygame.sprite.Group()
    all_sprites.add(
        bullet1_sprite,
        bullet2_sprite,
        tank1_sprite,
        tank2_sprite,
        terrain_sprite,
    )

    # Establish first frame positions
    tank1_sprite.update()
    tank2_sprite.update()
    bullet1_sprite.update()
    bullet2_sprite.update()

    senderSocket = createSenderSocket()
    receiverSocket = createReceiverSocket()
    receiverSocket.setblocking(False)

    # Current player in LAN mode is delayed
    if not LAN_GAME:
        # Choose a random player to start
        current_player: int = random.randint(1, 2)

    # Set frame limit variable
    frame_limit: int = FRAME_LIMIT
    # Explosion animation flags
    bullet_1_explosion: bool = False
    bullet_2_explosion: bool = False
    # Create a font object to use for drawing text
    font = pygame.font.Font(None, 36)
    # Signal to indicate game ended and present game over screen
    game_over = False
    # Variable that holds tank's ID of game winner
    game_winner = 0
    # Create a text surface to display the score
    text = font.render(f"Tank {game_winner} Won", True, colors.BLACK)
    # Get the dimensions of the rendered text
    text_rect = text.get_rect()
    # Set the position of the text so it is centered on the screen
    text_rect.center = (WIDTH * SCALE // 2, HEIGHT * SCALE // 2)
    # Run the game loop
    running: bool = True  # variable to control the game loop
    count: int = 0  # variable to keep track of number of iterations
    current_player_flag: bool = True  # variable to switch between players
    ready_flag: bool = True  # variable to check if the player is ready to start
    initialize_game_flag: bool = True  # variable to initialize the game
    OTHER_PLAYER_ID: int = 0  # variable to store the ID of the other player
    OTHER_PLAYER_NAME: str = "Tank 2"  # variable to store the name of the other player
    GAME_STARTING: bool = False  # variable to check if the game is starting
    PLAYER: bool = False  # variable to store the player number (False for player 1 and True for player 2)
    GAME_START: bool = False  # variable to check if the game has started
    SYNC_COMPLETE: bool = False  # variable to check if the synchronization is complete
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    return False

        if LAN_GAME:
            # If the game has not yet started
            if not GAME_STARTING:
                # If this is the first iteration of the loop
                if count == 0:
                    # Send a message to the sender socket indicating the user is waiting and working
                    sendMessage(
                        senderSocket,
                        pickle.dumps(
                            {
                                "user": USERNAME,
                                "id": USER_ID,
                                "status": "waiting",
                                "status2": "working",
                            }
                        ),
                    )
                    # Reset the count
                    count = FRAME_LIMIT
                # Decrement the count
                count -= 1
            # If the current player flag is set and the user is not the player
            elif current_player_flag and not PLAYER:
                # Reset the temp flag
                current_player_flag = False
                # Choose a random player to start
                current_player: int = random.randint(1, 2)
            # If the ready_flag flag is set and the user is not the player
            elif ready_flag and not PLAYER:
                # If this is the first iteration of the loop
                if count == 0:
                    # Send a message to the sender socket indicating the user is ready and the current player
                    sendMessage(
                        senderSocket,
                        pickle.dumps(
                            {
                                "user": USERNAME,
                                "id": USER_ID,
                                "status": "ready",
                                "current_player": current_player,
                            }
                        ),
                    )
                    # Reset the count
                    count = FRAME_LIMIT
                # Decrement the count
                count -= 1
            # If sync is not complete
            elif not SYNC_COMPLETE:
                # If this is the first iteration of the loop
                if count == 0:
                    # Send a message to the sender socket indicating the user is syncing
                    sendMessage(
                        senderSocket,
                        pickle.dumps(
                            {
                                "user": USERNAME,
                                "id": USER_ID,
                                "status": "sync",
                            }
                        ),
                    )
                    # Reset the count
                    count = FRAME_LIMIT
                # Decrement the count
                count -= 1
            # If the initialize_game_flag flag is set
            elif initialize_game_flag:
                # If the user is the player
                if PLAYER:
                    # Set the name of the first tank to the user's name
                    tank1_sprite.tank.set_tank_name(USERNAME)
                    # Set the name of the second tank to the other player's name
                    tank2_sprite.tank.set_tank_name(OTHER_PLAYER_NAME)
                    # Set the second tank to be the local player
                    tank2_sprite.tank.set_local_player(True)
                    # Set tank control to be qweasd
                    tank2_sprite.tank.set_controls(1)
                else:
                    # Set the name of the first tank to the other player's name
                    tank1_sprite.tank.set_tank_name(OTHER_PLAYER_NAME)
                    # Set the name of the second tank to the user's name
                    tank2_sprite.tank.set_tank_name(USERNAME)
                    # Set the first tank to be the local player
                    tank1_sprite.tank.set_local_player(True)
                    # Set tank control to be qweasd
                    tank2_sprite.tank.set_controls(1)
                # Set the current player flag for the chosen player
                if current_player == 1:
                    tank1_sprite.tank.current_player = True
                elif current_player == 2:
                    tank2_sprite.tank.current_player = True
                initialize_game_flag = False

            try:
                # Initialize the input keys list to all False
                input_keys = [False] * 512
                # Receive a message from the receiver socket
                if msg := receiverSocket.recvfrom(8192):
                    # Deserialize the message and store it in the userCommand dictionary
                    userCommand: dict = pickle.loads(msg[0])
                    # Get the ID of the user who sent the message
                    mc_user_id = userCommand.get("id")
                    # If the ID does not match the current user's ID
                    if mc_user_id != USER_ID:
                        # If the message includes a status field
                        if mc_user_status := userCommand.get("status"):
                            # If the status is "waiting" and sync has not yet been completed
                            if mc_user_status == "waiting" and (not SYNC_COMPLETE):
                                # Set the PLAYER flag based on the ID comparison
                                PLAYER = mc_user_id > USER_ID
                                # Store the other player's ID
                                OTHER_PLAYER_ID = mc_user_id
                                # Store the other player's name
                                OTHER_PLAYER_NAME = userCommand.get("user")
                                # Set the GAME_STARTING flag
                                GAME_STARTING = True
                                # Send a message to the sender socket indicating the user is waiting
                                sendMessage(
                                    senderSocket,
                                    pickle.dumps(
                                        {
                                            "user": USERNAME,
                                            "id": USER_ID,
                                            "status": "waiting",
                                        }
                                    ),
                                )
                    # If the ID of the user who sent the message matches the other player's ID
                    if mc_user_id == OTHER_PLAYER_ID:
                        # If the message includes a status field
                        if mc_user_status := userCommand.get("status"):
                            # If the status is "ready" and sync has not yet been completed
                            if (mc_user_status == "ready") and (not SYNC_COMPLETE):
                                # If the current user is the player
                                if PLAYER:
                                    # Store the current player
                                    current_player = userCommand.get("current_player")
                                # Set the GAME_START flag
                                GAME_START = True
                                # Reset the ready_flag flag
                                ready_flag = False
                                # Send a message to the sender socket indicating the user is ready and the current player
                                sendMessage(
                                    senderSocket,
                                    pickle.dumps(
                                        {
                                            "user": USERNAME,
                                            "id": USER_ID,
                                            "status": "ready",
                                            "current_player": current_player,
                                        }
                                    ),
                                )
                            # If the status is "sync" and sync has not yet been completed
                            elif (mc_user_status == "sync") and (not SYNC_COMPLETE):
                                # If the game has not yet started
                                if not GAME_START:
                                    # Send a message to the sender socket indicating the user is ready and the current player
                                    sendMessage(
                                        senderSocket,
                                        pickle.dumps(
                                            {
                                                "user": USERNAME,
                                                "id": USER_ID,
                                                "status": "ready",
                                                "current_player": current_player,
                                            }
                                        ),
                                    )
                                else:
                                    # Set the SYNC_COMPLETE flag
                                    SYNC_COMPLETE = True
                                    # Send a message to the sender socket indicating the user is ready to sync
                                    sendMessage(
                                        senderSocket,
                                        pickle.dumps(
                                            {
                                                "user": USERNAME,
                                                "id": USER_ID,
                                                "status": "sync",
                                            }
                                        ),
                                    )
                        # If the message includes a 'keys' field
                        elif mc_user_keys := userCommand.get("keys"):
                            # Update the input keys list with the keys sent by the other player
                            input_keys: list[int] = mc_user_keys
            except BlockingIOError:
                # Ignore when blocking
                pass

            if not SYNC_COMPLETE:
                # Draw the background image onto the window
                screen.blit(background_image, (-background_image_offset, 0))
                # Waiting for players text
                text = font.render("Waiting for players...", True, colors.BLACK)
                text_rect = text.get_rect()
                text_rect.center = (WIDTH * SCALE // 2, HEIGHT * SCALE // 2)
                # Blit the text surface to the screen
                screen.blit(text, text_rect)
                # Update screen
                pygame.display.flip()
                # Limit the frame rate
                clock.tick(frame_limit)
                continue

        # Update the game logic
        # Retrieve all keys that are being pressed
        keys_pressed: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        if LAN_GAME:
            keys: pygame.key.ScancodeWrapper = pygame.key.ScancodeWrapper(
                [a or b for a, b in zip(keys_pressed, input_keys, strict=False)]
            )
            if any(keys_pressed):
                sendMessage(
                    senderSocket,
                    pickle.dumps({"user": USERNAME, "id": USER_ID, "keys": keys}),
                )
        else:
            keys = keys_pressed

        # Check for collisions
        # Check if bullet1 is off the limits of the screen
        if check_off_limits(WIDTH * SCALE, bullet1_sprite.rect.centerx):
            # Set the flag indicating that bullet2 has hit something
            tank1_sprite.tank.bulletHit = True
        # Check if bullet1 has hit the second tank or hit the terrain
        elif bullet1_sprite.rect.colliderect(tank2_sprite.rect):
            # Set the flag indicating that bullet2 has hit something
            tank1_sprite.tank.bulletHit = True
            # Calculates and infliches damage to other tank
            tank2_sprite.tank.calculate_damage(bullet1_sprite.rect.center)
            # Bullet explosion animation flag
            bullet_1_explosion = True
            bullet1_sprite.bullet.set_bullet_hit_position(tank_hit=True)
        elif bullet1_sprite.rect.colliderect(terrain_sprite.rect):
            # Set the flag indicating that bullet2 has hit something
            tank1_sprite.tank.bulletHit = True
            # Calculates and infliches damage to other tank
            tank2_sprite.tank.calculate_damage(bullet1_sprite.rect.center)
            # Bullet explosion animation
            bullet_1_explosion = True
            # Set bullet 2 hit position
            bullet1_sprite.bullet.set_bullet_hit_position(
                pos=intersection(
                    bullet1_sprite.rect.bottomleft + bullet1_sprite.bullet.last_pos,
                    terrain_sprite.rect.topleft + terrain_sprite.rect.topright,
                ),
            )

            # Check if bullet2 is off the limits of the screen
        if check_off_limits(WIDTH * SCALE, bullet2_sprite.rect.centerx):
            # Set the flag indicating that bullet2 has hit something
            tank2_sprite.tank.bulletHit = True
        # Check if bullet2 has hit the second tank or hit the terrain
        elif bullet2_sprite.rect.colliderect(tank1_sprite.rect):
            # Set the flag indicating that bullet2 has hit something
            tank2_sprite.tank.bulletHit = True
            # Calculates and infliches damage to other tank
            tank1_sprite.tank.calculate_damage(bullet2_sprite.rect.center)
            # Bullet explosion animation
            bullet_2_explosion = True
            # Set bullet 2 hit position
            bullet2_sprite.bullet.set_bullet_hit_position(tank_hit=True)
        elif bullet2_sprite.rect.colliderect(terrain_sprite.rect):
            # Set the flag indicating that bullet2 has hit something
            tank2_sprite.tank.bulletHit = True
            # Calculates and infliches damage to other tank
            tank1_sprite.tank.calculate_damage(bullet2_sprite.rect.center)
            # Bullet explosion animation
            bullet_2_explosion = True
            # Set bullet 2 hit position
            bullet2_sprite.bullet.set_bullet_hit_position(
                pos=intersection(
                    bullet2_sprite.rect.bottomleft + bullet2_sprite.bullet.last_pos,
                    terrain_sprite.rect.topleft + terrain_sprite.rect.topright,
                ),
            )

            # Switch players
        if not tank1_sprite.tank.current_player and current_player == 1:
            # Switch to player 2
            current_player = 2
            # Tank2 can now move and prepare to shoot
            tank2_sprite.tank.current_player = True
        elif not tank2_sprite.tank.current_player and current_player == 2:
            # Switch to player 1
            current_player = 1
            # Tank1 can now move and prepare to shoot
            tank1_sprite.tank.current_player = True

        # Update tank information
        if not tank1_sprite.tank.update(keys):
            game_over = True
            game_winner = 2
        if not tank2_sprite.tank.update(keys):
            game_over = True
            game_winner = 1

        # Draw the background image onto the window
        screen.blit(background_image, (-background_image_offset, 0))

        # Update all sprites
        all_sprites.update()
        # Draw all sprites to screen
        all_sprites.draw(screen)

        # Draw preview lines for tank's bullets
        if current_player == 1 and not game_over:
            pygame.draw.line(
                screen,
                colors.BLACK,
                tank1_sprite.rect.center,
                (
                    tank1_sprite.rect.center[0]
                    + tank1_sprite.tank.bullet_power
                    * math.cos(tank1_sprite.tank.bullet_angle),
                    tank1_sprite.rect.center[1]
                    + tank1_sprite.tank.bullet_power
                    * math.sin(tank1_sprite.tank.bullet_angle),
                ),
            )
        elif current_player == 2 and not game_over:
            pygame.draw.line(
                screen,
                colors.BLACK,
                tank2_sprite.rect.center,
                (
                    tank2_sprite.rect.center[0]
                    + tank2_sprite.tank.bullet_power
                    * math.cos(tank2_sprite.tank.bullet_angle),
                    tank2_sprite.rect.center[1]
                    + tank2_sprite.tank.bullet_power
                    * math.sin(tank2_sprite.tank.bullet_angle),
                ),
            )

        # Draw tank1's name
        tank1_sprite.draw_name(screen)
        # Draw tank2's name
        tank2_sprite.draw_name(screen)

        # Draw tank1's health
        tank1_sprite.draw_health(screen)
        # Draw tank2's health
        tank2_sprite.draw_health(screen)

        if bullet_hit_animation(
            bullet_1_explosion,
            screen,
            explosion_sound,
            explosion_image,
            bullet1_sprite.bullet.bullet_hit_position,
        ):
            # If bullet 1 explosion animation has ended
            bullet_1_explosion = False
        if bullet_hit_animation(
            bullet_2_explosion,
            screen,
            explosion_sound,
            explosion_image,
            bullet2_sprite.bullet.bullet_hit_position,
        ):
            # If bullet 2 explosion animation has ended
            bullet_2_explosion = False

        if game_over:
            if LAN_GAME:
                # If the game is over, determine the winner based on the value of game_winner
                if not PLAYER:
                    # If the current player is not the user, set player_winner to the other player's name
                    player_winner = OTHER_PLAYER_NAME if game_winner == 1 else USERNAME
                # If the current player is the user, set player_winner to the user's name
                elif game_winner == 1:
                    player_winner = USERNAME
                elif game_winner == 2:
                    player_winner = OTHER_PLAYER_NAME

                # Create text surfaces to display the winner and a prompt to play again
                text = font.render(f"Player {player_winner} Won", True, colors.BLACK)
                text2 = font.render("Press R to play again", True, colors.BLACK)
                # Create rectangles for the text surfaces
                text_rect = text.get_rect()
                text_rect2 = text2.get_rect()
                # Set the rectangles to be centered on the screen
                text_rect.center = (WIDTH * SCALE // 2, HEIGHT * SCALE // 2)
                text_rect2.center = (
                    WIDTH * SCALE // 2,
                    HEIGHT * SCALE // 2 + text_rect.height,
                )
                # Blit the text surfaces to the screen
                screen.blit(text, text_rect)
                screen.blit(text2, text_rect2)
            else:
                player_winner = USERNAME if game_winner == 1 else OTHER_PLAYER_NAME
                text = font.render(f"Player {player_winner} Won", True, colors.BLACK)
                text_rect = text.get_rect()
                text_rect.center = (WIDTH * SCALE // 2, HEIGHT * SCALE // 2)
                screen.blit(text, text_rect)

        # Update screen
        pygame.display.flip()
        # Limit the frame rate
        clock.tick(frame_limit)

    return True


if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    # Initialize pygame mixer
    pygame.mixer.init()

    # Get player name
    USERNAME: str = str(input("Insert your name: "))
    USER_ID: int = random.random() * sys.maxsize
    LAN_GAME: int = int(input("Local or LAN game? (0 or 1): "))
    # Enter game
    while True:
        if main(64, 48, 10):
            break

    # Quit Pygame
    pygame.quit()
