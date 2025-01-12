import httpx
from typing import Optional
from .models import ProductInfo

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        
    async def get_product_info(self, scan_code: str) -> tuple[Optional[ProductInfo], Optional[str]]:
        try:
            # Configure httpx client with specific settings
            async with httpx.AsyncClient(
                timeout=30.0,
                verify=False,  # Try disabling SSL verification
                follow_redirects=True  # Allow redirects
            ) as client:
                response = await client.get(
                    f"{self.base_url}/products/{scan_code}",
                    headers={}  # Empty headers for now
                )
                response.raise_for_status()
                return ProductInfo.from_dict(response.json()), None
        except Exception as e:
            return None, f"Error: {str(e)}" 