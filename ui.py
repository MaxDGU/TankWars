"""
UI system for TankWars Single-Player Campaign
Menus, HUD, and game screens
"""

import pygame
import os

from config import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN,
                    YELLOW, GRAY, DARK_GRAY, PLAYER_START_HEALTH, LEVELS)


class UI:
    """User interface manager"""

    def __init__(self, screen):
        self.screen = screen
        self.screen_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Load fonts
        base_path = os.path.dirname(__file__)
        try:
            self.font_large = pygame.font.Font(os.path.join(base_path, "7theb.ttf"), 48)
            self.font_medium = pygame.font.Font(os.path.join(base_path, "7theb.ttf"), 32)
            self.font_small = pygame.font.Font(os.path.join(base_path, "7theb.ttf"), 18)
            self.font_hud = pygame.font.Font(os.path.join(base_path, "7theb.ttf"), 14)
        except pygame.error:
            # Fallback to system font
            self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
            self.font_medium = pygame.font.SysFont("Arial", 32, bold=True)
            self.font_small = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_hud = pygame.font.SysFont("Arial", 14, bold=True)

        # Menu state
        self.menu_selection = 0
        self.menu_options = ["New Game", "Continue", "Quit"]

        self.pause_selection = 0
        self.pause_options = ["Resume", "Restart Level", "Quit to Menu"]

    # ---------- Menu Navigation ----------

    def get_menu_selection(self):
        return self.menu_selection

    def menu_up(self):
        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)

    def menu_down(self):
        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)

    def get_pause_selection(self):
        return self.pause_selection

    def pause_up(self):
        self.pause_selection = (self.pause_selection - 1) % len(self.pause_options)

    def pause_down(self):
        self.pause_selection = (self.pause_selection + 1) % len(self.pause_options)

    # ---------- Drawing Methods ----------

    def _draw_text_centered(self, text, font, color, y_offset=0):
        """Draw text centered on screen"""
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(self.screen_center[0], self.screen_center[1] + y_offset))
        self.screen.blit(surface, rect)

    def _draw_text(self, text, font, color, pos):
        """Draw text at position"""
        surface = font.render(text, True, color)
        self.screen.blit(surface, pos)

    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(BLACK)

        # Title
        self._draw_text_centered("TANK WARS", self.font_large, WHITE, -120)
        self._draw_text_centered("Single Player Campaign", self.font_small, GRAY, -70)

        # Menu options
        for i, option in enumerate(self.menu_options):
            color = YELLOW if i == self.menu_selection else WHITE
            prefix = "> " if i == self.menu_selection else "  "
            self._draw_text_centered(prefix + option, self.font_medium, color, i * 50 - 20)

        # Instructions
        self._draw_text_centered("Use UP/DOWN to select, ENTER to confirm", self.font_small, GRAY, 150)

    def draw_pause_menu(self):
        """Draw pause menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Title
        self._draw_text_centered("PAUSED", self.font_large, WHITE, -80)

        # Menu options
        for i, option in enumerate(self.pause_options):
            color = YELLOW if i == self.pause_selection else WHITE
            prefix = "> " if i == self.pause_selection else "  "
            self._draw_text_centered(prefix + option, self.font_medium, color, i * 50)

    def draw_hud(self, player, score, lives, level, enemies_remaining):
        """Draw in-game HUD"""
        # Health bar background
        pygame.draw.rect(self.screen, DARK_GRAY, (10, 10, 104, 16))

        # Health bar
        if player and player.alive:
            health_width = int(100 * (player.health / PLAYER_START_HEALTH))
            health_color = self._get_health_color(player.health / PLAYER_START_HEALTH)
            pygame.draw.rect(self.screen, health_color, (12, 12, health_width, 12))

            # Health text
            self._draw_text(f"HP: {player.health}", self.font_hud, WHITE, (120, 10))

            # Ammo
            self._draw_text(f"Ammo: {player.ammo}", self.font_hud, YELLOW, (10, 32))

            # Active power-ups
            powerup_y = 54
            if player.shield_active:
                self._draw_text("SHIELD", self.font_hud, WHITE, (10, powerup_y))
                powerup_y += 18
            if player.speed_boost_active:
                self._draw_text("SPEED", self.font_hud, (0, 150, 255), (10, powerup_y))
                powerup_y += 18
            if player.rapid_fire_active:
                self._draw_text("RAPID", self.font_hud, (255, 128, 0), (10, powerup_y))
                powerup_y += 18
            if player.double_damage_active:
                self._draw_text("DAMAGE x2", self.font_hud, (255, 0, 255), (10, powerup_y))

        # Score (top right)
        score_text = f"Score: {score}"
        score_surface = self.font_hud.render(score_text, True, WHITE)
        self.screen.blit(score_surface, (SCREEN_WIDTH - score_surface.get_width() - 10, 10))

        # Lives
        lives_text = f"Lives: {lives}"
        lives_surface = self.font_hud.render(lives_text, True, WHITE)
        self.screen.blit(lives_surface, (SCREEN_WIDTH - lives_surface.get_width() - 10, 30))

        # Level info (top center)
        level_data = LEVELS.get(level, {})
        level_name = level_data.get("name", f"Level {level}")
        level_text = f"Level {level}: {level_name}"
        level_surface = self.font_hud.render(level_text, True, WHITE)
        self.screen.blit(level_surface, (SCREEN_WIDTH // 2 - level_surface.get_width() // 2, 10))

        # Enemies remaining
        enemies_text = f"Enemies: {enemies_remaining}"
        enemies_surface = self.font_hud.render(enemies_text, True, RED)
        self.screen.blit(enemies_surface, (SCREEN_WIDTH // 2 - enemies_surface.get_width() // 2, 30))

    def _get_health_color(self, health_ratio):
        """Get color based on health ratio (0-1)"""
        if health_ratio > 0.6:
            return GREEN
        elif health_ratio > 0.3:
            return YELLOW
        else:
            return RED

    def draw_level_complete(self, level, score):
        """Draw level complete screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Title
        self._draw_text_centered("LEVEL COMPLETE!", self.font_large, GREEN, -60)

        # Stats
        level_data = LEVELS.get(level, {})
        level_name = level_data.get("name", f"Level {level}")
        self._draw_text_centered(f"{level_name}", self.font_medium, WHITE, 0)
        self._draw_text_centered(f"Score: {score}", self.font_medium, YELLOW, 50)

        # Next level prompt
        if level < len(LEVELS):
            self._draw_text_centered("Press ENTER to continue", self.font_small, GRAY, 120)
        else:
            self._draw_text_centered("CAMPAIGN COMPLETE!", self.font_medium, YELLOW, 100)
            self._draw_text_centered("Press ENTER to continue", self.font_small, GRAY, 150)

    def draw_game_over(self, score, level_reached, game_won=False):
        """Draw game over screen"""
        self.screen.fill(BLACK)

        if game_won:
            self._draw_text_centered("VICTORY!", self.font_large, GREEN, -80)
            self._draw_text_centered("You completed the campaign!", self.font_medium, WHITE, -20)
        else:
            self._draw_text_centered("GAME OVER", self.font_large, RED, -80)
            self._draw_text_centered(f"Reached Level {level_reached}", self.font_medium, WHITE, -20)

        self._draw_text_centered(f"Final Score: {score}", self.font_medium, YELLOW, 40)
        self._draw_text_centered("Press ENTER for main menu", self.font_small, GRAY, 120)

    def draw_loading(self, level):
        """Draw loading screen"""
        self.screen.fill(BLACK)

        level_data = LEVELS.get(level, {})
        level_name = level_data.get("name", f"Level {level}")

        self._draw_text_centered(f"Level {level}", self.font_large, WHITE, -40)
        self._draw_text_centered(level_name, self.font_medium, YELLOW, 20)
        self._draw_text_centered("Loading...", self.font_small, GRAY, 80)

        pygame.display.flip()
