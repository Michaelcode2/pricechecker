import threading
from .fake_api import run_fake_api
import flet as ft
import sys
import os

# Add parent directory to path to import from pricechecker
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pricechecker.app import app

def main():
    # Start fake API in a separate thread
    api_thread = threading.Thread(target=run_fake_api, daemon=True)
    api_thread.start()
    
    # Run the main app
    ft.app(target=app.initialize)

if __name__ == "__main__":
    main()
    