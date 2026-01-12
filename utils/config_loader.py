import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def get_dropbox_config():
    config = load_config()
    return config.get('dropbox', {})

def get_google_drive_config():
    config = load_config()
    return config.get('google_drive', {})
