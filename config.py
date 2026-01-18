"""
config.py - Configuration and Settings Manager
Handles app settings, user preferences, and persistent storage
"""

import json
from pathlib import Path


class Config:
    """Configuration manager for Shot Ledger"""
    
    def __init__(self):
        # App data directory
        self.app_data_dir = Path.home() / "AppData" / "Local" / "ShotLedger"
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.config_file = self.app_data_dir / "config.json"
        self.session_file = self.app_data_dir / "Session_Data.xlsx"
        self.active_session_file = self.app_data_dir / "active_session.json"
        self.trash_dir = self.app_data_dir / "trash"  # Centralized trash (cleaner)
        self.trash_dir.mkdir(exist_ok=True)
        
        # Default settings
        self.default_config = {
            "last_project": "",
            "recent_projects": [],
            "camera_index": 0,
            "camera_resolution": "1920x1080",
            
            # File handling
            "duplicate_handling": "ask",  # ask, auto_increment, replace
            "empty_folder_handling": "keep",  # keep, delete, ask
            
            # Trash settings
            "use_trash": True,
            "auto_empty_trash": True,
            "undo_delete_limit": 10,  # Max undo deletions
            
            # Confirmations
            "confirm_delete": True,
            "confirm_end_session": True,
            "confirm_clear_log": True,
            
            # App behavior
            "on_exit": "keep_session",  # keep_session, end_session, ask
            "auto_focus_name": True,
            "status_duration": "permanent",  # 3sec, 5sec, permanent
            "subfolder_autocomplete": True,  # Show dropdown with existing subfolders
            
            # Performance
            "batch_save_interval": 1,  # Save every N photos (1 = every photo for safety)
            
            # UI
            "preview_size": 0.8,  # 80% of screen
            "theme": "dark"
        }
        
        # Load or create config
        self.settings = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.default_config, **loaded}
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def add_recent_project(self, path):
        """Add project to recent list"""
        path = str(path)
        
        # Remove if already exists
        if path in self.settings["recent_projects"]:
            self.settings["recent_projects"].remove(path)
        
        # Add to front
        self.settings["recent_projects"].insert(0, path)
        
        # Keep only last 5
        self.settings["recent_projects"] = self.settings["recent_projects"][:5]
        
        # Update last project
        self.settings["last_project"] = path
        
        # Save
        self.save_config()
    
    def get_setting(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value and save"""
        self.settings[key] = value
        return self.save_config()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.default_config.copy()
        return self.save_config()
    
    def get_camera_index(self):
        """Get current camera index"""
        return self.settings.get("camera_index", 0)
    
    def set_camera_index(self, index):
        """Set camera index"""
        self.settings["camera_index"] = index
        return self.save_config()
    
    def save_active_session(self, session_data):
        """Save active session info for crash recovery"""
        try:
            with open(self.active_session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving active session: {e}")
            return False
    
    def load_active_session(self):
        """Load active session info"""
        if self.active_session_file.exists():
            try:
                with open(self.active_session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading active session: {e}")
        return None
    
    def clear_active_session(self):
        """Clear active session file"""
        if self.active_session_file.exists():
            try:
                self.active_session_file.unlink()
                return True
            except Exception as e:
                print(f"Error clearing active session: {e}")
                return False
        return True