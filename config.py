"""
config.py - Configuration Manager
"""
import json
from pathlib import Path

class Config:
    def __init__(self):
        self.app_data_dir = Path.home() / "AppData" / "Local" / "ShotLedger"
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.app_data_dir / "config.json"
        self.session_file = self.app_data_dir / "Session_Data.xlsx"
        
        self.default_config = {
            "last_project": "",
            "recent_projects": [],
            "camera_index": 0,
            "use_trash": True,
        }
        self.settings = self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return {**self.default_config, **json.load(f)}
        return self.default_config.copy()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def add_recent_project(self, path):
        if path in self.settings["recent_projects"]:
            self.settings["recent_projects"].remove(path)
        self.settings["recent_projects"].insert(0, path)
        self.settings["recent_projects"] = self.settings["recent_projects"][:5]
        self.settings["last_project"] = path
        self.save_config()