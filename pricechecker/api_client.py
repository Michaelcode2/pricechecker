import httpx
from typing import Optional
from .models import ProductInfo
import flet as ft
from datetime import datetime
import asyncio

class APIClient:
    def __init__(self, base_url: str, api_key: str, status_text: Optional[ft.Text] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.status_text = status_text
        self.debug_messages = []
        
    async def show_debug(self, message: str):
        # Only print debug messages, don't show in UI
        print(f"[DEBUG] {message}")
        
    async def show_status(self, message: str, is_error: bool = False):
        if self.status_text:
            self.status_text.value = message
            self.status_text.color = "red" if is_error else "green"
            self.status_text.visible = True
            self.status_text.update()
        
    async def get_product_info(self, scan_code: str) -> tuple[Optional[ProductInfo], Optional[str]]:
        try:
            url = f"{self.base_url}/products/{scan_code}"
            headers = {"x-api-key": self.api_key} if self.api_key else {}
            
            async with httpx.AsyncClient(
                timeout=30.0,
                verify=False,
                follow_redirects=True
            ) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return ProductInfo.from_dict(response.json()), None
                
        except Exception as e:
            error = f"Error: {str(e)}"
            await self.show_status(error, is_error=True)
            return None, error 