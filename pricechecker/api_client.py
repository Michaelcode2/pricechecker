import httpx
from typing import Optional
from .models import ProductInfo

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        
    async def get_product_info(self, scan_code: str) -> tuple[Optional[ProductInfo], Optional[str]]:
        try:
            headers = {"x-api-key": self.api_key}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/products/{scan_code}",
                    headers=headers
                )
                response.raise_for_status()
                return ProductInfo.from_dict(response.json()), None
        except httpx.HTTPError as e:
            return None, f"API Error: {str(e)}"
        except Exception as e:
            return None, f"Error: {str(e)}" 