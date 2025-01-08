# pricechecker
Primitive price checker written on Flet framework

## Features
- Barcode scanning interface
- Product price lookup via API
- API key authentication via request headers
- Multilanguage support (English/Ukrainian)
- Keyboard blocking on main screen (for scanner devices)
- Scan history with last 10 items
- Configurable settings


### VENV

Activate environment after creation
`source .venv/bin/activate`


`libmpv.so` issue:

First, determine which version you have libmpv.so.*:

`locate libmpv.so`

My results:


```
/usr/lib/x86_64-linux-gnu/libmpv.so.2
/usr/lib/x86_64-linux-gnu/libmpv.so.2.2.0
```

Then you need to do this (in my case, it's libmpv.so.2):

`sudo ln -s /usr/lib/x86_64-linux-gnu/libmpv.so.2 /usr/lib/x86_64-linux-gnu/libmpv.so.1`


### Configuration

The application can be configured through the settings screen:
- API URL and authentication key
- Language selection (English/Ukrainian)
- Scan timeout and length parameters
- Keyboard toggle for scanner devices

### API Integration

The API expects requests with:
- `x-api-key` header for authentication
- Barcode in the request path

#### Endpoints

##### GET /products/{scan_code}
Retrieves product information by its barcode.

**Parameters:**
- `scan_code` (path parameter): The barcode number of the product

**Headers:**
- `x-api-key`: API authentication key

**Response:**
```json
{
    "name": "Product Name",
    "measurement": "pcs",
    "price": 10.99,
    "discountPrice": 8.99  // optional
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing API key
- `404 Not Found`: Product not found
- `500 Internal Server Error`: Server-side error

- - -

### Run application locally

To run application 

`python ./main.py`

To run application with mock server

`python -m pricechecker.mock_server.run_with_fake_api`

#### To run Android application in Flet emulator

`flet run --android`

Testing: https://flet.dev/docs/getting-started/testing-on-android/

