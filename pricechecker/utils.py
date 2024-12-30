import flet as ft
from datetime import datetime
from .models import ProductInfo

def create_history_item(barcode: str, product: ProductInfo, timestamp: datetime = None):
    if timestamp is None:
        timestamp = datetime.now()
    
    # Create base column controls
    column_controls = [
        ft.Text(
            f"Scanned: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            size=12,
            color=ft.colors.GREY_700
        ),
        ft.Text(product.name, size=16, weight=ft.FontWeight.BOLD),
        ft.Text(f"Barcode: {barcode}"),
        ft.Text(f"Price: ${product.price:.2f}")
    ]
    
    # Add discount field only if there is a discount
    if product.discount_price:
        column_controls.append(
            ft.Text(f"Discount: ${product.discount_price:.2f}")
        )
    
    return ft.Card(
        content=ft.Container(
            content=ft.Column(column_controls, spacing=5),
            padding=10,
            expand=True
        ),
        width=None,
        expand=True
    )