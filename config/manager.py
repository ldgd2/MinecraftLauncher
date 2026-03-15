import json
import os
from core.paths import get_config_path

CONFIG_FILE = get_config_path()

DEFAULT_CONFIG = {
    "username": "Player",
    "ram_mb": 4096,
    "java_path": "",
    "jvm_arguments": "-XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M",
    "minecraft_dir": os.path.join(os.getenv("APPDATA", ""), ".custom_mc_launcher"),
    "selected_version": "",
    "selected_type": "Vanilla"
}

class ConfigManager:
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.load()
        
        if not os.path.exists(CONFIG_FILE):
            self.save()
        # Determine the minecraft directory. If APPDATA is not available, use local dir.
        if not self.config["minecraft_dir"]:
            self.config["minecraft_dir"] = os.path.abspath(".custom_mc_launcher")

        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # Update existing config with loaded values (keeps new defaults if added later)
                    for key, value in loaded_config.items():
                        if key in self.config:
                            self.config[key] = value
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")

        # Ensure directory exists
        os.makedirs(self.config["minecraft_dir"], exist_ok=True)

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.config.get(key)

    def set(self, key, value):
        if key in self.config:
            self.config[key] = value
            self.save()

# Global singleton
config = ConfigManager()
