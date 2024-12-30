import flet as ft
from datetime import datetime
from .handlers import handle_scan
from .utils import create_history_item
from .api_client import APIClient
from .models import ProductInfo
import json  # Add this import at the top

class HistoryView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        
        # Create a container for history items
        self.history_container = ft.Container(
            content=ft.ListView(
                spacing=10,
                expand=True,
            ),
            padding=10,
            expand=True
        )
        
        # Set the view's controls with Stack layout
        self.controls = [
            ft.Stack(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.IconButton(ft.icons.ARROW_BACK, on_click=self.go_back),
                                            ft.Text("Scan History", size=20, weight=ft.FontWeight.BOLD),
                                            ft.IconButton(ft.icons.DELETE_OUTLINE, on_click=self.clear_history),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    bgcolor=ft.colors.SURFACE_VARIANT,
                                    padding=10,
                                ),
                                self.history_container
                            ],
                            spacing=0,
                            expand=True
                        ),
                        expand=True
                    )
                ],
                expand=True
            )
        ]
        
        # Load existing history
        self.load_history()
    
    def load_history(self):
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
                    self.history_container.content.controls.append(history_item)
        except Exception as e:
            print(f"Error loading history: {e}")
    
    async def clear_history(self, _):
        try:
            print("Clearing history...")
            # Clear storage using set instead of remove to ensure it's empty
            await self.page.client_storage.set_async("scan_history", "[]")
            
            # Verify the storage is cleared - use async version
            current_storage = await self.page.client_storage.get_async("scan_history")
            #print(f"Storage after clearing: {current_storage}")
            
            # Clear ListView
            self.history_container.content.controls.clear()
            self.history_container.content.update()
            
            # Update main view's history
            for view in self.page.views:
                if isinstance(view, MainView):
                    view.history = []
                    break
                    
            self.page.update()
        except Exception as e:
            print(f"Error clearing history: {e}")
            #raise e  # This will help us see the full error if something goes wrong
    
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
        # Load existing history from storage
        try:
            saved_history = page.client_storage.get("scan_history")
            self.history = json.loads(saved_history) if saved_history else []
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []
        
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
                
                # Save to storage using async
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
                        view.history_container.content.controls.insert(0, history_item)
                        view.history_container.content.controls = view.history_container.content.controls[:10]
                        view.history_container.content.update()  # Update the ListView
                        view.history_container.update()  # Update the container
                        view.update()  # Update the entire view
                        self.page.update()  # Update the page
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
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.window_width = 400
        
        # Setup routing
        self.main_view = MainView(page)
        
        def route_change(route):
            self.page.views.clear()
            if page.route == "/history":
                # Create a new HistoryView each time we navigate to it
                self.history_view = HistoryView(page)
                self.page.views.append(self.history_view)
            else:
                self.page.views.append(self.main_view)
            self.page.update()
            
        self.page.on_route_change = route_change
        self.page.go('/')

app = ScannerApp()