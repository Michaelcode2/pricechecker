import flet as ft
import json
from datetime import datetime
from .handlers import handle_scan
from .utils import create_history_item
from .api_client import APIClient
from .models import ProductInfo
from .languages import TRANSLATIONS


class HistoryView(ft.View):
    def __init__(self, page: ft.Page, language: str):
        super().__init__()
        self.page = page
        self.language = language
        
        # Create a container for history items
        self.history_container = ft.Container(
            content=ft.ListView(
                spacing=10,
                expand=True,
            ),
            padding=10,
            expand=True
        )
        
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
                                            ft.Text(TRANSLATIONS[self.language]["scan_history"], size=20, weight=ft.FontWeight.BOLD),
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
                        TRANSLATIONS[self.language],
                        datetime.fromisoformat(item["timestamp"])
                    )
                    self.history_container.content.controls.append(history_item)
        except Exception as e:
            print(f"Error loading history: {e}")
    
    async def clear_history(self, _):
        try:
            await self.page.client_storage.set_async("scan_history", "[]")
            
            current_storage = await self.page.client_storage.get_async("scan_history")
            
            self.history_container.content.controls.clear()
            self.history_container.content.update()
            
            for view in self.page.views:
                if isinstance(view, MainView):
                    view.history = []
                    break
                    
            self.page.update()
        except Exception as e:
            print(f"Error clearing history: {e}")
            raise e 
    
    def go_back(self, _):
        self.page.go('/')

class ProductInfoCard(ft.Card):
    def __init__(self, language: str = "ukr"):
        super().__init__()
        self.t = TRANSLATIONS[language]
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(self.t["no_product"], size=16),
                ],
                spacing=10,
            ),
            padding=15,
        )
        
    def update_info(self, product: ProductInfo):
        self.content.content.controls = [
            ft.Text(
                product.name,
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            
            ft.Row(
                [
                    ft.Text(self.t["measurement"], size=14, color=ft.colors.GREY_700),
                    ft.Text(product.measurement, size=14),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text(self.t["price"], size=20),
                        ft.Text(
                            f"{product.price:.2f}",
                            size=36,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLACK,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(vertical=10),
            ),
        ]
        
        if product.discount_price:
            self.content.content.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                self.t["special_offer"],
                                size=16,
                                color=ft.colors.RED,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        f"{product.discount_price:.2f}",
                                        size=36,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.RED,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(top=10),
                )
            )
        self.update()

class MainView(ft.View):
    def __init__(self, page: ft.Page, language: str = "en"):

        super().__init__(route="/")
        
        # Set instance variables
        self.page = page
        self.language = language
        self.t = TRANSLATIONS[language]
        
        # Load settings
        settings = self.load_settings()
        self.api_client = APIClient(
            settings.get("api_url", "http://127.0.0.1:8000"),
            settings.get("api_key", "")
        )
        self.product_card = ProductInfoCard(language)
        
        # Load existing history from storage
        try:
            saved_history = page.client_storage.get("scan_history")
            self.history = json.loads(saved_history) if saved_history else []
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []
        
        # Set up controls
        self.controls = [
            ft.Stack([
                ft.Column([
                    ft.Text(self.t["app_title"], size=24, weight=ft.FontWeight.BOLD),
                    ft.Column([
                        ft.Row([
                            ft.TextField(
                                label=self.t["scan_here"],
                                width=None,
                                expand=True,
                                autofocus=True,
                                on_submit=self.on_scan,
                                multiline=False,
                                text_size=18,
                                keyboard_type=ft.KeyboardType.NONE,
                            ),
                            ft.IconButton(
                                icon=ft.icons.KEYBOARD,
                                on_click=self.toggle_keyboard,
                                tooltip="Toggle keyboard",
                            ),
                            ft.ElevatedButton(
                                self.t["submit"],
                                on_click=self.on_scan,
                                width=100,
                                height=50,
                                style=ft.ButtonStyle(
                                    padding=ft.padding.all(15),
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=10),
                        ft.Text(
                            size=16,
                            color=ft.colors.GREY_700
                        ),
                        self.product_card,
                    ], spacing=10),
                ], spacing=10, expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            self.t["view_history"],
                            on_click=lambda _: page.go("/history"),
                            width=200,
                            height=50,
                        ),
                        ft.ElevatedButton(
                            self.t["settings"],
                            on_click=self.show_settings_dialog,
                            width=200,
                            height=50,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10),
                    alignment=ft.alignment.center,
                    bottom=20,
                    left=0,
                    right=0,
                ),
            ], expand=True)
        ]
        
        self.scan_field = self.controls[0].controls[0].controls[1].controls[0].controls[0]
        self.status_text = self.controls[0].controls[0].controls[1].controls[1]
        
        # Add keyboard listener to the page
        self.page.on_keyboard_event = self.handle_keyboard_event
        
        # Add dialog definition
        self.settings_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(TRANSLATIONS[self.language]["settings_confirm"]),
            content=ft.Text(TRANSLATIONS[self.language]["settings_confirm"]),
            actions=[
                ft.TextButton(TRANSLATIONS[self.language]["yes"], on_click=self.open_settings),
                ft.TextButton(TRANSLATIONS[self.language]["no"], on_click=self.close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def handle_keyboard_event(self, e: ft.KeyboardEvent):
        """Handle keyboard events globally"""
        try:
            # Check if page and route exist before accessing
            if hasattr(self, 'page') and self.page and self.page.route == "/":
                self.scan_field.focus()
                self.page.update()
        except Exception as e:
            print(f"Error handling keyboard event: {e}")
    
    async def on_scan(self, e):
        if not self.scan_field.value:
            return
            
        # Get product info from API
        product, error = await self.api_client.get_product_info(self.scan_field.value)
        
        if error:
            self.status_text.value = error
            self.status_text.color = "red"
        else:
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
                self.history.insert(0, new_item)
                self.history = self.history[:10]  # Keep only last 10
                
                await self.page.client_storage.set_async("scan_history", json.dumps(self.history))
                
                # Create and add history item to view
                history_item = create_history_item(
                    new_item["barcode"], 
                    product,
                    TRANSLATIONS[self.language],
                    datetime.fromisoformat(new_item["timestamp"])
                )
                
                # Update history view if it exists
                for view in self.page.views:
                    if isinstance(view, HistoryView):
                        view.history_container.content.controls.insert(0, history_item)
                        view.history_container.content.controls = view.history_container.content.controls[:10]
                        view.history_container.content.update() 
                        view.history_container.update()
                        view.update()
                        self.page.update()
                        break
                
                self.status_text.value = TRANSLATIONS[self.language]["scan_successful"]
                self.status_text.color = "green"
                
            except Exception as e:
                print(f"Error saving to storage: {e}")
                self.status_text.value = TRANSLATIONS[self.language]["error_saving"]
                self.status_text.color = "red"
            
        self.scan_field.value = ""
        self.scan_field.keyboard_type = ft.KeyboardType.NONE 
        self.scan_field.update()
        self.page.update()
        self.scan_field.focus()
    
    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
                return settings
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "language": "ukr", 
                "max_scan_length": 14,
                "min_scan_length": 6
            }
    
    def show_settings_dialog(self, _):
        self.page.dialog = self.settings_dialog
        self.settings_dialog.open = True
        self.page.update()
    
    def close_dialog(self, _):
        self.settings_dialog.open = False
        self.page.update()
    
    def open_settings(self, _):
        self.settings_dialog.open = False
        self.page.update()
        self.page.go("/config")
    
    def toggle_keyboard(self, _):
        """Toggle between number keyboard and no keyboard"""
        current_type = self.scan_field.keyboard_type
        new_type = (
            ft.KeyboardType.NUMBER 
            if current_type == ft.KeyboardType.NONE 
            else ft.KeyboardType.NONE
        )
        
        self.scan_field.keyboard_type = new_type
        self.page.show_keyboard = (new_type == ft.KeyboardType.NUMBER)
        self.page.update()
        self.scan_field.focus()


class ConfigView(ft.View):
    def __init__(self, page: ft.Page, language: str):
        super().__init__()
        self.page = page
        self.language = language
        
        # Load saved settings
        self.settings = self.load_settings()
        
        # Create input fields
        self.api_url_field = ft.TextField(
            label=TRANSLATIONS[self.language]["api_url"],
            value=self.settings.get("api_url", "http://127.0.0.1:8000"),
            width=None,
            expand=True
        )
        
        self.scan_timeout_field = ft.TextField(
            label=TRANSLATIONS[self.language]["scan_timeout"],
            value=str(self.settings.get("scan_timeout", 1.0)),
            width=None,
            expand=True
        )
        
        self.min_length_field = ft.TextField(
            label=TRANSLATIONS[self.language]["min_length"],
            value=str(self.settings.get("min_scan_length", 4)),
            width=None,
            expand=True
        )
        
        self.max_length_field = ft.TextField(
            label=TRANSLATIONS[self.language]["max_length"],
            value=str(self.settings.get("max_scan_length", 14)),
            width=None,
            expand=True
        )

        # Add language dropdown
        self.language_dropdown = ft.Dropdown(
            label=TRANSLATIONS[self.language]["language"],
            width=None,
            expand=True,
            value=self.language,
            options=[
                ft.dropdown.Option("ukr", "Українська"),
                ft.dropdown.Option("en", "English"),
            ],
        )

        self.api_key_field = ft.TextField(
            label=TRANSLATIONS[self.language]["api_key"],
            value=self.settings.get("api_key", ""),
            width=None,
            expand=True,
            password=True  # Hide the API key
        )

        def handle_save(_):
            async def _save():
                await self.save_settings(_)
            self.page.add_async(_save())
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.IconButton(ft.icons.ARROW_BACK, on_click=self.go_back),
                                ft.Text(TRANSLATIONS[self.language]["settings"], size=20, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    ft.icons.SAVE,
                                    on_click=self.save_settings
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        padding=10,
                    ),
                    
                    ft.Container(
                        content=ft.Column([
                            self.language_dropdown,
                            self.api_url_field,
                            self.api_key_field,
                            self.scan_timeout_field,
                            self.min_length_field,
                            self.max_length_field,
                        ], 
                        spacing=20,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=20,
                    ),
                ],
                spacing=0,
                expand=True,
                ),
                expand=True,
            )
        ]

    def load_settings(self):
        try:
            saved_settings = self.page.client_storage.get("app_settings")
            return json.loads(saved_settings) if saved_settings else {}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def go_back(self, _):
        if not self.page:
            return
            
        # Store page reference
        page = self.page
        
        # Remove this view before navigation
        if self in page.views:
            page.views.remove(self)
            
        page.update()
        page.go('/')

    def save_settings(self, _):
        if not self.page:
            return
            
        # Store page reference
        page = self.page
            
        try:
            settings = {
                "api_url": self.api_url_field.value,
                "api_key": self.api_key_field.value,
                "scan_timeout": float(self.scan_timeout_field.value),
                "min_scan_length": int(self.min_length_field.value),
                "max_scan_length": int(self.max_length_field.value),
                "language": self.language_dropdown.value
            }
            
            # Save settings
            page.client_storage.set("app_settings", json.dumps(settings))
            
            # Update MainView settings
            for view in page.views:
                if isinstance(view, MainView):
                    view.api_client = APIClient(
                        settings["api_url"],
                        settings["api_key"]
                    )
                    break
            
            # Remove this view before navigation
            if self in page.views:
                page.views.remove(self)
            
            # Navigate and show success message
            page.go('/')
            page.snack_bar = ft.SnackBar(
                content=ft.Text(TRANSLATIONS[self.language]["settings_saved"]),
                duration=1000,
            )
            page.snack_bar.open = True
            page.update()

        except Exception as e:
            print(f"Error saving settings: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error saving settings: {str(e)}"),
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()

class ScannerApp:
    def __init__(self):
        self.page = None
        self.language = "ukr"  # Default language
        
    def initialize(self, page: ft.Page):
        self.page = page
        self.page.title = "Scanner Input"
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.window_width = 400
        
        # disable back button
        self.page.on_view_pop = lambda _: None
        
        # Store app instance in page data for access from other views
        self.page.data = {"app": self}
        
        # Load saved settings
        try:
            saved_settings = page.client_storage.get("app_settings")
            settings = json.loads(saved_settings) if saved_settings else {}
            self.language = settings.get("language", "ukr")
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.language = "ukr"
        
        # Setup routing
        self.main_view = MainView(page, self.language)
        
        def route_change(route):
            #print(f"Route changed to: {route.route}")  # Debug print
            self.page.views.clear()
            
            if route.route == "/history":
                self.page.views.append(HistoryView(page, self.language))
            elif route.route == "/config":
                self.page.views.append(ConfigView(page, self.language))
            else:
                self.page.views.append(self.main_view)
                
            self.page.update()
        
        self.page.on_route_change = route_change
        self.page.go('/')
    
    async def change_language(self, new_lang):
        self.language = new_lang
        await self.page.client_storage.set_async("language", new_lang)
        # Update all views
        self.main_view = MainView(self.page, self.language)
        self.page.appbar.title.value = TRANSLATIONS[self.language]["app_title"]
        self.page.go(self.page.route)  # Refresh current route

app = ScannerApp()