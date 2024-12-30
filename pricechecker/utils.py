import flet as ft
from datetime import datetime
from .models import ProductInfo

def create_history_item(scan_code: str, product: ProductInfo = None) -> ft.Container:
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    content = [
        ft.Row([
            ft.Text(f"Code: {scan_code}", size=14),
            ft.Text(timestamp, size=12, color=ft.colors.GREY_700),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ]
    
    if product:
        content.extend([
            ft.Text(product.name, size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Text(f"${product.price:.2f}", size=14),
                ft.Text(product.measurement, size=14),
            ]),
        ])
        
        if product.discount_price:
            content.append(
                ft.Text(
                    f"Discount: ${product.discount_price:.2f}",
                    size=14,
                    color=ft.colors.RED
                )
            )
    
    return ft.Container(
        content=ft.Column(content, spacing=4),
        bgcolor=ft.colors.BLUE_GREY_50,
        padding=10,
        border_radius=8,
    )