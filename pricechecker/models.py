from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductInfo:
    name: str
    measurement: str
    price: float
    discount_price: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get('name', ''),
            measurement=data.get('measurement', ''),
            price=float(data.get('price', 0)),
            discount_price=float(data.get('discountPrice', 0)) if data.get('discountPrice') else None
        ) 