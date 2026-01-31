"""
Enemy AI system for TankWars Single-Player Campaign
"""

import pygame
import os
import random
import math
from pygame.locals import *
from math import sin, cos, radians, atan2, degrees

from config import ENEMY_TYPES
from effects import Bullet, Boom


class EnemyBullet(pygame.sprite.Sprite):
    """Bullet fired by enemies"""

    def __init__(self, pos, angle, size, groups):
        pygame.sprite.Sprite.__init__(self)

        self._size = size
        self.tank = -1  # Enemy bullet marker

        if self._size == "big":
            self.b_size = (2, 7)
            self.speed = 16
        else:
            self.b_size = (1, 3)
            self.speed = 20

        self.image = pygame.Surface(self.b_size)
        self.image.fill((255, 100, 0))  # Orange for enemy bullets
        self.image.set_colorkey((0, 0, 0), RLEACCEL)

        self.rect = self.image.get_rect(center=pos)
        self.x, self.y = self.rect.center

        # Offset from cannon
        cannon_dist = 25
        self.x -= sin(radians(angle)) * cannon_dist
        self.y -= cos(radians(angle)) * cannon_dist
        self.rect.center = (self.x, self.y)

        self.angle = angle
        self.image = pygame.transform.rotate(self.image, angle)

        # Add to groups
        for group in groups:
            group.add(self)

    def get_size(self):
        return self._size

    def update(self, bricks, booms):
        """Update bullet position"""
        self.x += -sin(radians(self.angle)) * self.speed
        self.y += -cos(radians(self.angle)) * self.speed
        self.rect.center = (self.x, self.y)

        # Check brick collision
        for brick in bricks:
            if self.rect.colliderect(brick.rect):
                pygame.sprite.Sprite.kill(self)
                booms.add(Boom(self.rect.center, self._size))
                return

        # Remove if off screen
        if self.x < -50 or self.x > 1300 or self.y < -50 or self.y > 600:
            pygame.sprite.Sprite.kill(self)


class Enemy(pygame.sprite.Sprite):
    """Base enemy tank with AI"""

    def __init__(self, pos, enemy_type, bricks, bullets_group, allgroup):
        pygame.sprite.Sprite.__init__(self)

        self.enemy_type = enemy_type
        config = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["scout"])

        # Stats from config
        self.health = config["health"]
        self.max_health = config["health"]
        self.speed = config["speed"]
        self.fire_delay = config["fire_delay"]
        self.accuracy = config["accuracy"]
        self.points = config["points"]
        self.behavior = config["behavior"]
        self.bullet_size = config.get("bullet_size", "small")
        self.color = config["color"]

        # Position and movement
        self.x, self.y = pos
        self.angle = random.randint(0, 360)
        self.target_angle = self.angle
        self.turn_speed = 2

        # Combat
        self.fire_timer = random.randint(0, self.fire_delay)  # Stagger initial shots
        self.alive = True

        # AI state
        self.ai_state = "patrol"
        self.patrol_direction = 1
        self.patrol_timer = 0
        self.pursue_distance = 300
        self.attack_distance = 400

        # Create colored tank image
        base_path = os.path.dirname(__file__)
        self.tank_pic = pygame.image.load(os.path.join(base_path, "tank2.png")).convert_alpha()
        self._image = self._tint_image(self.tank_pic, self.color)
        self.image = self._image

        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        # References
        self.bricks = bricks
        self.bullets_group = bullets_group
        self.allgroup = allgroup

        # Patrol waypoints (generated based on position)
        self.waypoints = self._generate_waypoints()
        self.current_waypoint = 0

    def _tint_image(self, image, color):
        """Tint an image with a color"""
        tinted = image.copy()
        tinted.fill(color + (0,), special_flags=pygame.BLEND_RGB_ADD)
        return tinted

    def _generate_waypoints(self):
        """Generate patrol waypoints around spawn position"""
        waypoints = []
        for _ in range(4):
            wx = self.x + random.randint(-150, 150)
            wy = self.y + random.randint(-100, 100)
            # Clamp to screen bounds
            wx = max(50, min(1120, wx))
            wy = max(50, min(460, wy))
            waypoints.append((wx, wy))
        return waypoints

    def rotate(self):
        """Rotate tank sprite"""
        center = self.rect.center
        self.image = pygame.transform.rotozoom(self._image, self.angle, 1.0)
        self.rect = self.image.get_rect(center=center)

    def update(self, player, bricks, player_bullets, booms):
        """Update enemy AI and state"""
        if not self.alive or self.health <= 0:
            return

        # Get distance and angle to player
        player_dist = 9999
        player_angle = 0

        if player and player.alive:
            dx = player.x - self.x
            dy = player.y - self.y
            player_dist = math.sqrt(dx * dx + dy * dy)
            player_angle = degrees(atan2(-dx, -dy))

        # Update AI based on behavior type
        if self.behavior == "stationary":
            self._ai_stationary(player, player_dist, player_angle)
        elif self.behavior == "boss":
            self._ai_boss(player, player_dist, player_angle)
        else:
            self._ai_patrol_pursue(player, player_dist, player_angle)

        # Smoothly turn toward target angle
        angle_diff = self.target_angle - self.angle
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360

        if abs(angle_diff) > self.turn_speed:
            self.angle += self.turn_speed if angle_diff > 0 else -self.turn_speed
        else:
            self.angle = self.target_angle

        # Normalize angle
        while self.angle > 360:
            self.angle -= 360
        while self.angle < 0:
            self.angle += 360

        # Update visual
        self.rotate()
        self.rect.center = (self.x, self.y)

        # Handle brick collision
        self._handle_brick_collision()

        # Handle player bullet collision
        self._handle_bullet_collision(player_bullets, booms)

        # Update fire timer
        self.fire_timer += 1

        # Check death
        if self.health <= 0:
            self.alive = False

    def _ai_stationary(self, player, player_dist, player_angle):
        """Stationary sniper AI - just aim and shoot"""
        if player and player.alive and player_dist < self.attack_distance:
            self.target_angle = player_angle
            self._try_fire(player_angle)

    def _ai_patrol_pursue(self, player, player_dist, player_angle):
        """Patrol and pursue AI"""
        if player and player.alive and player_dist < self.pursue_distance:
            # Pursue mode
            self.ai_state = "pursue"
            self.target_angle = player_angle

            # Move toward player
            if self.speed > 0 and player_dist > 100:
                self.x += sin(radians(self.angle)) * -self.speed
                self.y += cos(radians(self.angle)) * -self.speed

            # Try to fire at player
            if player_dist < self.attack_distance:
                self._try_fire(player_angle)
        else:
            # Patrol mode
            self.ai_state = "patrol"
            self._patrol()

    def _ai_boss(self, player, player_dist, player_angle):
        """Boss AI - aggressive pursuit with frequent attacks"""
        if player and player.alive:
            self.target_angle = player_angle

            # Move toward player but keep some distance
            if self.speed > 0:
                if player_dist > 200:
                    self.x += sin(radians(self.angle)) * -self.speed
                    self.y += cos(radians(self.angle)) * -self.speed
                elif player_dist < 100:
                    # Back up if too close
                    self.x += sin(radians(self.angle)) * self.speed
                    self.y += cos(radians(self.angle)) * self.speed

            # Fire frequently
            self._try_fire(player_angle)

    def _patrol(self):
        """Patrol between waypoints"""
        if not self.waypoints:
            return

        target = self.waypoints[self.current_waypoint]
        dx = target[0] - self.x
        dy = target[1] - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 30:
            # Reached waypoint, go to next
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)
        else:
            # Move toward waypoint
            self.target_angle = degrees(atan2(-dx, -dy))
            if self.speed > 0:
                self.x += sin(radians(self.angle)) * -self.speed * 0.5  # Slower patrol
                self.y += cos(radians(self.angle)) * -self.speed * 0.5

    def _try_fire(self, target_angle):
        """Try to fire at target angle with accuracy variance"""
        if self.fire_timer >= self.fire_delay:
            self.fire_timer = 0

            # Add inaccuracy
            accuracy_offset = (1 - self.accuracy) * 30
            fire_angle = target_angle + random.uniform(-accuracy_offset, accuracy_offset)

            # Create enemy bullet
            EnemyBullet(
                self.rect.center,
                fire_angle,
                self.bullet_size,
                [self.bullets_group, self.allgroup]
            )

    def _handle_brick_collision(self):
        """Handle collision with bricks"""
        prev_x, prev_y = self.x, self.y

        for brick in self.bricks:
            if self.rect.colliderect(brick.rect):
                # Simple push-back
                dx = self.rect.centerx - brick.rect.centerx
                dy = self.rect.centery - brick.rect.centery

                if abs(dx) > abs(dy):
                    self.x = prev_x
                else:
                    self.y = prev_y

                # Change patrol direction on collision
                if self.ai_state == "patrol":
                    self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)

        self.rect.center = (self.x, self.y)

    def _handle_bullet_collision(self, player_bullets, booms):
        """Handle collision with player bullets (done in main game loop)"""
        pass

    def take_damage(self, amount):
        """Take damage"""
        self.health -= amount
        if self.health <= 0:
            self.alive = False


def spawn_enemies(enemy_list, bricks, enemies_group, bullets_group, allgroup, map_size):
    """Spawn enemies for a level

    Args:
        enemy_list: List of tuples (enemy_type, count)
        bricks: Brick sprite group for collision
        enemies_group: Group to add enemies to
        bullets_group: Group for enemy bullets
        allgroup: Master sprite group
        map_size: (width, height) of map
    """
    spawn_positions = []

    # Generate spawn positions on right side of map (away from player)
    map_width, map_height = map_size

    for enemy_type, count in enemy_list:
        for _ in range(count):
            # Try to find valid spawn position
            for attempt in range(50):
                x = random.randint(int(map_width * 0.5), int(map_width * 0.9))
                y = random.randint(50, map_height - 50)

                # Check not too close to other spawns
                valid = True
                for sx, sy in spawn_positions:
                    if abs(x - sx) < 60 and abs(y - sy) < 60:
                        valid = False
                        break

                # Check not inside a brick
                temp_rect = pygame.Rect(x - 20, y - 20, 40, 40)
                for brick in bricks:
                    if temp_rect.colliderect(brick.rect):
                        valid = False
                        break

                if valid:
                    spawn_positions.append((x, y))
                    enemy = Enemy((x, y), enemy_type, bricks, bullets_group, allgroup)
                    enemies_group.add(enemy)
                    break
