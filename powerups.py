"""
Power-up system for TankWars Single-Player Campaign
"""

import pygame
import random

from config import POWERUP_TYPES, POWERUP_DROP_CHANCE


class PowerUp(pygame.sprite.Sprite):
    """Collectible power-up item"""

    def __init__(self, pos, powerup_type):
        pygame.sprite.Sprite.__init__(self)

        self.powerup_type = powerup_type
        self.config = POWERUP_TYPES.get(powerup_type, POWERUP_TYPES["health"])

        # Visual
        self.size = 24
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(self.config["color"])

        # Draw symbol
        font = pygame.font.SysFont("Arial", 16, bold=True)
        symbol = font.render(self.config["symbol"], True, (0, 0, 0))
        symbol_rect = symbol.get_rect(center=(self.size // 2, self.size // 2))
        self.image.blit(symbol, symbol_rect)

        self.rect = self.image.get_rect(center=pos)

        # Animation
        self.animation_timer = 0
        self.base_y = pos[1]

        # Lifetime (disappears after a while)
        self.lifetime = 600  # 25 seconds at 24 FPS

    def update(self):
        """Update power-up animation and lifetime"""
        # Bobbing animation
        self.animation_timer += 1
        bob_offset = int(3 * pygame.math.Vector2(0, 1).rotate(self.animation_timer * 6).y)
        self.rect.centery = self.base_y + bob_offset

        # Reduce lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

        # Flashing when about to expire
        if self.lifetime < 72:  # 3 seconds
            if (self.lifetime // 6) % 2 == 0:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)

    def apply(self, player):
        """Apply power-up effect to player

        Args:
            player: PlayerTank instance
        """
        effect = self.config["effect"]
        value = self.config["value"]
        duration = self.config["duration"]

        if effect == "restore_health":
            player.apply_health(value)
        elif effect == "restore_ammo":
            player.apply_ammo(value)
        elif effect == "speed_boost":
            player.apply_speed_boost(duration)
        elif effect == "invulnerability":
            player.apply_shield(duration)
        elif effect == "rapid_fire":
            player.apply_rapid_fire(duration)
        elif effect == "double_damage":
            player.apply_double_damage(duration)


class PowerUpManager:
    """Manages power-up spawning"""

    def __init__(self):
        self.powerup_types = list(POWERUP_TYPES.keys())

    def try_spawn_from_enemy(self, pos, powerups_group):
        """Try to spawn a power-up when enemy is destroyed

        Args:
            pos: Position to spawn at
            powerups_group: Sprite group to add power-up to

        Returns:
            PowerUp or None
        """
        if random.random() < POWERUP_DROP_CHANCE:
            powerup_type = random.choice(self.powerup_types)
            powerup = PowerUp(pos, powerup_type)
            powerups_group.add(powerup)
            return powerup
        return None

    def try_random_spawn(self, bricks, powerups_group, map_size):
        """Try to spawn a power-up at a random valid location

        Args:
            bricks: Brick sprite group for collision checking
            powerups_group: Sprite group to add power-up to
            map_size: (width, height) of map

        Returns:
            PowerUp or None
        """
        # 50% chance to spawn
        if random.random() > 0.5:
            return None

        map_width, map_height = map_size

        # Try to find valid position
        for _ in range(20):
            x = random.randint(100, map_width - 100)
            y = random.randint(100, map_height - 100)

            # Check not inside a brick
            temp_rect = pygame.Rect(x - 15, y - 15, 30, 30)
            valid = True

            for brick in bricks:
                if temp_rect.colliderect(brick.rect):
                    valid = False
                    break

            if valid:
                powerup_type = random.choice(self.powerup_types)
                powerup = PowerUp((x, y), powerup_type)
                powerups_group.add(powerup)
                return powerup

        return None

    def spawn_specific(self, pos, powerup_type, powerups_group):
        """Spawn a specific type of power-up

        Args:
            pos: Position to spawn at
            powerup_type: Type of power-up
            powerups_group: Sprite group to add to

        Returns:
            PowerUp
        """
        powerup = PowerUp(pos, powerup_type)
        powerups_group.add(powerup)
        return powerup
