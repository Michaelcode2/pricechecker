from fastapi import FastAPI, HTTPException, Header
from typing import Optional
import uvicorn
from random import uniform, choice

app = FastAPI()

# Expected API key
VALID_API_KEY = "12345"

# Fake database of products
FAKE_PRODUCTS = {
    "12345678900014": {
        "name": "Test Product 1",
        "measurement": "pcs",
        "price": 9.99,
        "discountPrice": 7.99
    },
    "98765432145555": {
        "name": "Test Product 2",
        "measurement": "kg",
        "price": 15.50,
        "discountPrice": None
    },
    # Add more test products as needed
}

# Random product generator for unknown barcodes
def generate_random_product(barcode: str):
    measurements = ["pcs", "kg", "l", "m"]
    return {
        "name": f"Random Product {barcode[-4:]}",
        "measurement": choice(measurements),
        "price": round(uniform(1.0, 100.0), 2),
        "discountPrice": round(uniform(1.0, 100.0), 2) if choice([True, False]) else None
    }

@app.get("/products/{barcode}")
async def get_product(barcode: str, x_api_key: Optional[str] = Header(None)):
    # Validate API key
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Return predefined product if exists
    if barcode in FAKE_PRODUCTS:
        return FAKE_PRODUCTS[barcode]
    
    # Generate random product for unknown barcodes
    return generate_random_product(barcode)

def run_fake_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_fake_api()