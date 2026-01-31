"""
TankWars Single-Player Campaign
Main entry point with game state machine
"""

import pygame
import sys
import os
from pygame.locals import *

from config import *
from player import PlayerTank
from enemies import Enemy, spawn_enemies
from levels import LevelManager
from ui import UI
from powerups import PowerUp, PowerUpManager
from effects import Bullet, Boom, Fireball, Blast

# Set up pygame
pygame.init()
pygame.mixer.init()


class Brick(pygame.sprite.Sprite):
    """Brick obstacle from map"""

    def __init__(self, pos, image, top, bottom, right, left, bricks):
        pygame.sprite.Sprite.__init__(self)
        self.rect = image.get_rect(topleft=pos)
        self.image = image
        self.pos = pos
        self.top = top
        self.bottom = bottom
        self.right = right
        self.left = left
        self.health = 30
        bricks.add(self)


class City(object):
    """Map loader - creates bricks from PNG image"""

    def __init__(self, bricks, level_image):
        self.level = level_image
        self.city = self.level.convert_alpha()
        self.brick = pygame.image.load(os.path.join(os.path.dirname(__file__), "brick.png")).convert_alpha()
        self.bricks = bricks

        self.x = self.y = 0
        self.height = self.city.get_height()
        self.width = self.city.get_width()

        while self.y < self.height:
            color = self.city.get_at((self.x, self.y))
            collidable = ((255, 0, 0, 255), (0, 0, 0, 255))
            top = bottom = right = left = False

            if color in collidable:
                if self.y > 0:
                    if self.city.get_at((self.x, self.y - 1)) not in collidable:
                        top = True
                if self.y < self.height - 1:
                    if self.city.get_at((self.x, self.y + 1)) not in collidable:
                        bottom = True
                if self.x > 0:
                    if self.city.get_at((self.x - 1, self.y)) not in collidable:
                        left = True
                if self.x < self.width - 1:
                    if self.city.get_at((self.x + 1, self.y)) not in collidable:
                        right = True
                self.bricks.add(Brick((self.x * 30, self.y * 30), self.brick,
                                      top, bottom, right, left, self.bricks))

            self.x += 1
            if self.x >= self.width:
                self.x = 0
                self.y += 1

    def get_size(self):
        return [self.city.get_size()[0] * 30, self.city.get_size()[1] * 30]


class Game:
    """Main game class with state machine"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        pygame.display.set_caption("Tank Wars - Single Player Campaign")
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()
        self.state = STATE_MENU

        # Sprite groups
        self.bricks = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.booms = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.allgroup = pygame.sprite.LayeredUpdates()

        # Set up sprite groups for Bullet class
        Bullet.groups = self.bullets, self.allgroup

        # Game managers
        self.level_manager = LevelManager()
        self.powerup_manager = PowerUpManager()
        self.ui = UI(self.screen)

        # Player
        self.player = None

        # Game state
        self.score = 0
        self.lives = PLAYER_START_LIVES
        self.current_level = 1
        self.paused = False

        # City/Map
        self.city = None
        self.background = None

        # Timer for power-up spawns
        self.powerup_timer = 0

    def reset_groups(self):
        """Clear all sprite groups"""
        self.bricks.empty()
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.booms.empty()
        self.bombs.empty()
        self.enemies.empty()
        self.powerups.empty()
        self.allgroup.empty()

    def load_level(self, level_num):
        """Load a specific level"""
        self.reset_groups()

        level_data = LEVELS.get(level_num)
        if not level_data:
            # Game complete!
            self.state = STATE_GAME_OVER
            return False

        # Try to load level map, fall back to default maps if not found
        map_path = os.path.join(os.path.dirname(__file__), "maps", level_data["map"])
        if not os.path.exists(map_path):
            # Fall back to existing maps
            fallback_maps = ["c2.png", "a2.png"]
            map_path = os.path.join(os.path.dirname(__file__), fallback_maps[(level_num - 1) % 2])

        try:
            map_image = pygame.image.load(map_path)
        except pygame.error:
            # Use default map if level map not found
            map_path = os.path.join(os.path.dirname(__file__), "c2.png")
            map_image = pygame.image.load(map_path)

        self.city = City(self.bricks, map_image)
        city_size = self.city.get_size()
        self.background = pygame.Surface(city_size, 0, 32)

        # Create player
        start_pos = level_data.get("player_start", (100, 250))
        if self.player:
            # Preserve player stats between levels
            health = min(self.player.health + 10, PLAYER_START_HEALTH)  # Heal 10 HP between levels
            ammo = self.player.ammo + 30  # Restore some ammo
        else:
            health = PLAYER_START_HEALTH
            ammo = PLAYER_START_AMMO

        self.player = PlayerTank(start_pos, 90, health, ammo, self.bullets, self.allgroup)

        # Spawn enemies
        spawn_enemies(level_data["enemies"], self.bricks, self.enemies,
                      self.enemy_bullets, self.allgroup, city_size)

        self.current_level = level_num
        self.powerup_timer = 0

        return True

    def start_new_game(self):
        """Start a new game from level 1"""
        self.score = 0
        self.lives = PLAYER_START_LIVES
        self.current_level = 1
        self.player = None
        self.level_manager.reset()
        self.load_level(1)
        self.state = STATE_PLAYING

    def continue_game(self):
        """Continue from last saved checkpoint"""
        saved_level = self.level_manager.load_progress()
        self.current_level = saved_level
        self.score = 0
        self.lives = PLAYER_START_LIVES
        self.player = None
        self.load_level(saved_level)
        self.state = STATE_PLAYING

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                    elif self.state == STATE_MENU:
                        return False

                # Menu navigation
                if self.state == STATE_MENU:
                    if event.key == K_RETURN:
                        selection = self.ui.get_menu_selection()
                        if selection == 0:  # New Game
                            self.start_new_game()
                        elif selection == 1:  # Continue
                            self.continue_game()
                        elif selection == 2:  # Quit
                            return False
                    elif event.key == K_UP:
                        self.ui.menu_up()
                    elif event.key == K_DOWN:
                        self.ui.menu_down()

                # Pause menu navigation
                elif self.state == STATE_PAUSED:
                    if event.key == K_RETURN:
                        selection = self.ui.get_pause_selection()
                        if selection == 0:  # Resume
                            self.state = STATE_PLAYING
                        elif selection == 1:  # Restart Level
                            self.load_level(self.current_level)
                            self.state = STATE_PLAYING
                        elif selection == 2:  # Quit to Menu
                            self.state = STATE_MENU
                    elif event.key == K_UP:
                        self.ui.pause_up()
                    elif event.key == K_DOWN:
                        self.ui.pause_down()

                # Level complete
                elif self.state == STATE_LEVEL_COMPLETE:
                    if event.key == K_RETURN:
                        self.level_manager.save_progress(self.current_level + 1)
                        if not self.load_level(self.current_level + 1):
                            # No more levels - game complete!
                            self.state = STATE_GAME_OVER
                        else:
                            self.state = STATE_PLAYING

                # Game over
                elif self.state == STATE_GAME_OVER:
                    if event.key == K_RETURN:
                        self.state = STATE_MENU

        return True

    def update_playing(self):
        """Update game state while playing"""
        keys = pygame.key.get_pressed()

        # Update player
        if self.player and self.player.alive:
            self.player.update(keys, self.bricks, self.enemy_bullets, self.booms, self.bombs)

            # Check player death
            if not self.player.alive or self.player.health <= 0:
                self.lives -= 1
                self.booms.add(Boom(self.player.rect.center, "huge"))

                if self.lives <= 0:
                    self.state = STATE_GAME_OVER
                else:
                    # Respawn player
                    level_data = LEVELS.get(self.current_level, {})
                    start_pos = level_data.get("player_start", (100, 250))
                    self.player = PlayerTank(start_pos, 90, PLAYER_START_HEALTH,
                                            PLAYER_START_AMMO, self.bullets, self.allgroup)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.player, self.bricks, self.bullets, self.booms)

            # Check if enemy destroyed
            if not enemy.alive or enemy.health <= 0:
                self.score += enemy.points
                self.booms.add(Boom(enemy.rect.center, "large"))

                # Chance to spawn power-up
                self.powerup_manager.try_spawn_from_enemy(enemy.rect.center, self.powerups)

                enemy.kill()

        # Update bullets
        self.bullets.update(self.bricks, self.booms)
        self.enemy_bullets.update(self.bricks, self.booms)

        # Check bullet-enemy collisions
        for bullet in self.bullets:
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    damage = 2 if self.player.double_damage_active else 1
                    enemy.take_damage(damage)
                    bullet.kill()
                    self.booms.add(Boom(bullet.rect.center, "small"))
                    break

        # Update power-ups
        self.powerups.update()

        # Check power-up collisions with player
        if self.player and self.player.alive:
            for powerup in self.powerups:
                if self.player.rect.colliderect(powerup.rect):
                    powerup.apply(self.player)
                    powerup.kill()

        # Random power-up spawns
        self.powerup_timer += 1
        if self.powerup_timer >= POWERUP_SPAWN_INTERVAL:
            self.powerup_timer = 0
            self.powerup_manager.try_random_spawn(self.bricks, self.powerups,
                                                   (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Update explosions
        self.booms.update(self.screen)
        self.bombs.update(self.booms, self.player)

        # Check level complete
        if len(self.enemies) == 0:
            self.state = STATE_LEVEL_COMPLETE

    def render_playing(self):
        """Render game while playing"""
        self.screen.fill(BLACK)

        # Draw map
        self.city.bricks.draw(self.screen)

        # Draw player
        if self.player and self.player.alive:
            self.screen.blit(self.player.image, self.player.rect)

        # Draw enemies
        for enemy in self.enemies:
            self.screen.blit(enemy.image, enemy.rect)

        # Draw bullets
        self.bullets.draw(self.screen)
        self.enemy_bullets.draw(self.screen)

        # Draw power-ups
        self.powerups.draw(self.screen)

        # Draw explosions
        self.bombs.draw(self.screen)

        # Draw HUD
        self.ui.draw_hud(self.player, self.score, self.lives,
                        self.current_level, len(self.enemies))

    def run(self):
        """Main game loop"""
        running = True

        while running:
            running = self.handle_events()

            if self.state == STATE_MENU:
                self.ui.draw_menu()

            elif self.state == STATE_PLAYING:
                self.update_playing()
                self.render_playing()

            elif self.state == STATE_PAUSED:
                self.render_playing()  # Show game in background
                self.ui.draw_pause_menu()

            elif self.state == STATE_LEVEL_COMPLETE:
                self.render_playing()
                self.ui.draw_level_complete(self.current_level, self.score)

            elif self.state == STATE_GAME_OVER:
                game_won = self.current_level > len(LEVELS)
                self.ui.draw_game_over(self.score, self.current_level, game_won)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
