# pricechecker
Primitive price checker written on Flet framework


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


### Processing

Obtained data:
- name
- measurement
- price
- discountPrice


#### Run mock API

Returns

````
{
    "name": "Product Name",
    "measurement": "pcs",
    "price": 10.99,
    "discountPrice": 8.99  // optional
}
```

To run application with mock server

`python -m pricechecker.mock_server.run_with_fake_api`

Test barcodes:

12345678900014

98765432145555


