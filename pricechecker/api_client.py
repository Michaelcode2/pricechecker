import httpx
from typing import Optional
from .models import ProductInfo

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    async def get_product_info(self, scan_code: str) -> tuple[Optional[ProductInfo], Optional[str]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/products/{scan_code}")
                response.raise_for_status()
                return ProductInfo.from_dict(response.json()), None
        except httpx.HTTPError as e:
            return None, f"API Error: {str(e)}"
        except Exception as e:
            return None, f"Error: {str(e)}" 