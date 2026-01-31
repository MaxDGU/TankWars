"""
Player Tank class for TankWars Single-Player Campaign
"""

import pygame
import os
from pygame.locals import *
from math import sin, cos, radians

from config import (PLAYER_SPEED, PLAYER_TURN_SPEED, PLAYER_FIRE_DELAY,
                    PLAYER_START_HEALTH)
from effects import Bullet, Boom


class PlayerTank(pygame.sprite.Sprite):
    """Player-controlled tank"""

    def __init__(self, pos, angle, health, ammo, bullets_group, allgroup):
        pygame.sprite.Sprite.__init__(self)

        # Position and movement
        self.x, self.y = pos
        self.angle = angle
        self.speed = PLAYER_SPEED
        self.turn_speed = PLAYER_TURN_SPEED

        # Stats
        self.health = health
        self.max_health = PLAYER_START_HEALTH
        self.ammo = ammo
        self.alive = True

        # Combat
        self.fire_delay = PLAYER_FIRE_DELAY
        self.fire_timer = self.fire_delay  # Ready to fire immediately
        self.bullet_size = "small"
        self.damage_multiplier = 1

        # Power-up effects
        self.speed_boost_timer = 0
        self.shield_timer = 0
        self.rapid_fire_timer = 0
        self.double_damage_timer = 0

        self.speed_boost_active = False
        self.shield_active = False
        self.rapid_fire_active = False
        self.double_damage_active = False

        # Visual
        base_path = os.path.dirname(__file__)
        self.tank_pic = pygame.image.load(os.path.join(base_path, "tank2.png")).convert_alpha()
        self.image = self.tank_pic
        self._image = self.tank_pic
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        # Sound
        self.bullet_sound = pygame.mixer.Sound(os.path.join(base_path, "bullet.wav"))
        self.bullet_sound.set_volume(0.25)

        # References
        self.bullets_group = bullets_group
        self.allgroup = allgroup

        # Set up Bullet groups
        Bullet.groups = bullets_group, allgroup

        # Control keys
        self.forward_key = K_w
        self.backward_key = K_s
        self.left_key = K_a
        self.right_key = K_d
        self.fire_key = K_SPACE

    def rotate(self):
        """Rotate tank sprite to match angle"""
        center = self.rect.center
        self.image = pygame.transform.rotozoom(self._image, self.angle, 1.0)
        self.rect = self.image.get_rect(center=center)

    def update(self, keys, bricks, enemy_bullets, booms, bombs):
        """Update player tank state"""
        if not self.alive:
            return

        # Store previous position for collision
        prev_rect = self.rect.copy()
        prev_rect.center = (self.x, self.y)

        # Update power-up timers
        self._update_powerups()

        # Calculate current speed (with boost if active)
        current_speed = self.speed * (1.5 if self.speed_boost_active else 1.0)
        current_fire_delay = self.fire_delay * (0.5 if self.rapid_fire_active else 1.0)

        # Handle movement
        pressed = pygame.key.get_pressed()

        if pressed[self.forward_key]:
            self.x += sin(radians(self.angle)) * -current_speed
            self.y += cos(radians(self.angle)) * -current_speed

        if pressed[self.backward_key]:
            self.x += sin(radians(self.angle)) * current_speed
            self.y += cos(radians(self.angle)) * current_speed

        if pressed[self.left_key]:
            self.angle += self.turn_speed

        if pressed[self.right_key]:
            self.angle -= self.turn_speed

        # Normalize angle
        if self.angle > 360:
            self.angle -= 360
        if self.angle < 0:
            self.angle += 360

        # Update visual rotation
        self.rotate()
        self.rect.center = (self.x, self.y)

        # Handle firing
        self.fire_timer += 1
        if pressed[self.fire_key]:
            if self.fire_timer >= current_fire_delay and self.ammo > 0:
                self.fire_timer = 0
                self._fire()

        # Handle brick collisions
        self._handle_brick_collision(bricks, prev_rect)

        # Handle enemy bullet collisions
        if not self.shield_active:
            self._handle_bullet_collision(enemy_bullets, booms)

        # Handle bomb collisions
        self._handle_bomb_collision(bombs)

        # Check death
        if self.health <= 0:
            self.alive = False
            self.health = 0

    def _update_powerups(self):
        """Update power-up timers"""
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost_active = False

        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False

        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer <= 0:
                self.rapid_fire_active = False

        if self.double_damage_timer > 0:
            self.double_damage_timer -= 1
            if self.double_damage_timer <= 0:
                self.double_damage_active = False

    def _fire(self):
        """Fire a bullet"""
        bullet = Bullet(
            self.rect.center,
            self.angle,
            self.bullet_size,
            "player",
            0  # Player tank ID
        )
        self.bullets_group.add(bullet)
        self.ammo -= 1
        self.bullet_sound.play()

    def _handle_brick_collision(self, bricks, prev_rect):
        """Handle collision with bricks"""
        x = self.rect.centerx
        y = self.rect.centery
        prev_x = prev_rect.centerx
        prev_y = prev_rect.centery

        for brick in bricks:
            if self.rect.colliderect(brick.rect):
                # Check which side we hit from
                if prev_x + 21 <= brick.rect.left and x + 21 > brick.rect.left:
                    if brick.left:
                        self.x = brick.rect.left - 21
                if prev_x - 21 >= brick.rect.right and x - 21 < brick.rect.right:
                    if brick.right:
                        self.x = brick.rect.right + 21
                if prev_y + 21 <= brick.rect.top and y + 21 > brick.rect.top:
                    if brick.top:
                        self.y = brick.rect.top - 21
                if prev_y - 21 >= brick.rect.bottom and y - 21 < brick.rect.bottom:
                    if brick.bottom:
                        self.y = brick.rect.bottom + 21

        self.rect.center = (self.x, self.y)

    def _handle_bullet_collision(self, enemy_bullets, booms):
        """Handle collision with enemy bullets"""
        for bullet in enemy_bullets:
            if self.rect.colliderect(bullet.rect):
                bullet_size = bullet.get_size()
                pygame.sprite.Sprite.kill(bullet)

                if bullet_size == "small":
                    booms.add(Boom(bullet.rect.center, "small"))
                    self.health -= 1
                elif bullet_size == "big":
                    booms.add(Boom(bullet.rect.center, "big"))
                    self.health -= 5

    def _handle_bomb_collision(self, bombs):
        """Handle collision with bombs"""
        for bomb in bombs:
            if self.rect.colliderect(bomb.rect) and hasattr(bomb, 'timer') and bomb.timer == 20:
                if not self.shield_active:
                    self.health -= 5

    # Power-up application methods
    def apply_health(self, value):
        """Restore health"""
        self.health = min(self.health + value, self.max_health)

    def apply_ammo(self, value):
        """Restore ammo"""
        self.ammo += value

    def apply_speed_boost(self, duration):
        """Apply speed boost"""
        self.speed_boost_active = True
        self.speed_boost_timer = duration

    def apply_shield(self, duration):
        """Apply invulnerability shield"""
        self.shield_active = True
        self.shield_timer = duration

    def apply_rapid_fire(self, duration):
        """Apply rapid fire"""
        self.rapid_fire_active = True
        self.rapid_fire_timer = duration

    def apply_double_damage(self, duration):
        """Apply double damage"""
        self.double_damage_active = True
        self.double_damage_timer = duration
