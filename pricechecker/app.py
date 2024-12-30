import flet as ft
from datetime import datetime
from .handlers import handle_scan
from .utils import create_history_item
from .api_client import APIClient
from .models import ProductInfo
import json  # Add this import at the top

class HistoryView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            "/history",
            [
                ft.AppBar(
                    title=ft.Text("History"),
                    leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=self.go_back),
                ),
                ft.Column(
                    scroll=ft.ScrollMode.ALWAYS,
                    expand=True,
                    spacing=5,
                )
            ],
            padding=10,
            spacing=10
        )
        self.page = page
        self.history_column = self.controls[1]
        
        # Load saved history when view is created
        try:
            saved_history = self.page.client_storage.get("scan_history")
            if saved_history:
                history = json.loads(saved_history)
                for item in history:
                    product = ProductInfo(**item["product"])
                    history_item = create_history_item(
                        item["barcode"], 
                        product,
                        datetime.fromisoformat(item["timestamp"])
                    )
                    self.history_column.controls.append(history_item)
        except Exception as e:
            print(f"Error loading history: {e}")
    
    def go_back(self, _):
        self.page.go('/')

class ProductInfoCard(ft.Card):
    def __init__(self):
        super().__init__()
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("No product scanned", size=16),
                ],
                spacing=10,
            ),
            padding=15,
        )
        
    def update_info(self, product: ProductInfo):
        self.content.content.controls = [
            ft.Text(product.name, size=18, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Text("Measurement:", size=14),
                ft.Text(product.measurement, size=14),
            ]),
            ft.Row([
                ft.Text("Price:", size=16),
                ft.Text(f"${product.price:.2f}", size=16, weight=ft.FontWeight.BOLD),
            ]),
        ]
        
        if product.discount_price:
            self.content.content.controls.append(
                ft.Row([
                    ft.Text("Discount Price:", size=16, color=ft.colors.RED),
                    ft.Text(
                        f"${product.discount_price:.2f}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.RED
                    ),
                ])
            )
        self.update()

class MainView(ft.View):
    def __init__(self, page: ft.Page):
        self.api_client = APIClient("http://127.0.0.1:8000")
        self.product_card = ProductInfoCard()
        self.history = []  # Initialize empty history
        
        super().__init__(
            "/",
            [
                ft.Stack(
                    [
                        ft.Column([
                            ft.Text("Price Checker", size=24, weight=ft.FontWeight.BOLD),
                            ft.Column([
                                ft.Row(
                                    [
                                        ft.TextField(
                                            label="Scan here",
                                            width=None,
                                            expand=True,
                                            autofocus=True,
                                            on_submit=self.on_scan,
                                            multiline=False,
                                            text_size=18,
                                        ),
                                        ft.ElevatedButton(
                                            "Submit",
                                            on_click=self.on_scan,
                                            width=100,
                                            height=50,
                                            style=ft.ButtonStyle(
                                                padding=ft.padding.all(15),
                                            ),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    spacing=10,
                                ),
                                ft.Text(
                                    size=16,
                                    color=ft.colors.GREY_700
                                ),
                                self.product_card,
                            ], spacing=10),
                        ], spacing=10, expand=True),
                        ft.Container(
                            content=ft.ElevatedButton(
                                "View History",
                                on_click=lambda _: page.go("/history"),
                                width=200,
                                height=50,
                            ),
                            alignment=ft.alignment.center,
                            bottom=20,
                            left=0,
                            right=0,
                        ),
                    ],
                    expand=True
                )
            ],
            padding=10,
            spacing=10
        )
        self.page = page
        self.scan_field = self.controls[0].controls[0].controls[1].controls[0].controls[0]
        self.status_text = self.controls[0].controls[0].controls[1].controls[1]
        
    async def on_scan(self, e):
        if not self.scan_field.value:
            return
            
        # Get product info from API
        product, error = await self.api_client.get_product_info(self.scan_field.value)
        
        if error:
            self.status_text.value = error
            self.status_text.color = "red"
        else:
            # Update product info card
            self.product_card.update_info(product)
            
            # Create new history item
            new_item = {
                "barcode": self.scan_field.value,
                "product": {
                    "name": product.name,
                    "measurement": product.measurement,
                    "price": product.price,
                    "discount_price": product.discount_price
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to storage
            try:
                # Add new item to history
                self.history.insert(0, new_item)
                self.history = self.history[:10]  # Keep only last 10
                
                # Save to storage
                await self.page.client_storage.set_async("scan_history", json.dumps(self.history))
                
                # Create and add history item to view
                history_item = create_history_item(
                    new_item["barcode"], 
                    product,
                    datetime.fromisoformat(new_item["timestamp"])
                )
                
                # Update history view if it exists
                for view in self.page.views:
                    if isinstance(view, HistoryView):
                        view.history_column.controls.insert(0, history_item)
                        view.history_column.controls = view.history_column.controls[:10]
                        view.update()
                        break
                
                self.status_text.value = "Scan successful"
                self.status_text.color = "green"
                
            except Exception as e:
                print(f"Error saving to storage: {e}")
                self.status_text.value = "Error saving history"
                self.status_text.color = "red"
            
        self.scan_field.value = ""
        self.page.update()
        self.scan_field.focus()

class ScannerApp:
    def __init__(self):
        self.page = None
        
    def initialize(self, page: ft.Page):
        self.page = page
        self.page.title = "Scanner Input"
        self.page.padding = 0  # Removed padding since views have their own padding
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.window_width = 400
        
        # Setup routing
        self.main_view = MainView(page)
        self.history_view = HistoryView(page)
        
        self.page.views.append(self.main_view)
        self.page.views.append(self.history_view)
        
        def route_change(route):
            self.page.views.clear()
            if page.route == "/history":
                self.page.views.append(self.history_view)
            else:
                self.page.views.append(self.main_view)
            self.page.update()
            
        self.page.on_route_change = route_change
        self.page.go('/')

app = ScannerApp()