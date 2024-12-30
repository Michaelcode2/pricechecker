import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App settings
APP_NAME = "Scanner App"
DEBUG = True

# Database settings
DB_PATH = os.path.join('data', 'scans.db')

# Scanner settings
SCAN_TIMEOUT = 1.0  # seconds
MIN_SCAN_LENGTH = 12
MAX_SCAN_LENGTH = 13