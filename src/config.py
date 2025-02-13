# src/config.py
from os import getenv
from pathlib import Path

# API Configuration
SCRYFALL_API_URL = getenv('SCRYFALL_API_URL', 'https://api.scryfall.com')
GOOGLE_VISION_CREDENTIALS = getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Application Settings
CSV_PATH = Path(getenv('CSV_PATH', 'cards.csv'))
MAX_BATCH_SIZE = int(getenv('MAX_BATCH_SIZE', 10))
CAMERA_RESOLUTION = (
    int(getenv('CAMERA_WIDTH', 640)),
    int(getenv('CAMERA_HEIGHT', 480))
)

# FastAPI Settings
API_HOST = getenv('API_HOST', '0.0.0.0')
API_PORT = int(getenv('API_PORT', 8000))
API_RELOAD = getenv('API_RELOAD', 'True').lower() == 'true'