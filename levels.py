"""
Level management for TankWars Single-Player Campaign
"""

import json
import os
from config import SAVE_FILE, LEVELS


class LevelManager:
    """Manages level progression and save/load"""

    def __init__(self):
        self.current_level = 1
        self.highest_level = 1
        self.save_path = os.path.join(os.path.dirname(__file__), SAVE_FILE)

    def reset(self):
        """Reset to level 1"""
        self.current_level = 1

    def get_level_data(self, level_num):
        """Get configuration for a level

        Args:
            level_num: Level number (1-10)

        Returns:
            dict: Level configuration or None if level doesn't exist
        """
        return LEVELS.get(level_num)

    def get_level_name(self, level_num):
        """Get display name for a level"""
        level_data = self.get_level_data(level_num)
        if level_data:
            return level_data.get("name", f"Level {level_num}")
        return f"Level {level_num}"

    def get_total_levels(self):
        """Get total number of levels"""
        return len(LEVELS)

    def is_final_level(self, level_num):
        """Check if this is the final level"""
        return level_num >= len(LEVELS)

    def save_progress(self, level_num):
        """Save progress (checkpoint at level)

        Args:
            level_num: Highest level reached
        """
        try:
            data = {
                "highest_level": max(level_num, self.highest_level)
            }
            with open(self.save_path, 'w') as f:
                json.dump(data, f)
            self.highest_level = data["highest_level"]
        except (IOError, OSError) as e:
            print(f"Could not save progress: {e}")

    def load_progress(self):
        """Load saved progress

        Returns:
            int: Highest level reached (1 if no save file)
        """
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                self.highest_level = data.get("highest_level", 1)
                return self.highest_level
        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Could not load progress: {e}")

        return 1

    def has_save_file(self):
        """Check if a save file exists"""
        return os.path.exists(self.save_path)

    def delete_save(self):
        """Delete save file"""
        try:
            if os.path.exists(self.save_path):
                os.remove(self.save_path)
        except OSError:
            pass
