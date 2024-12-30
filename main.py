import flet as ft
from pricechecker.app import app

def main(page: ft.Page):
    app.initialize(page)

if __name__ == "__main__":
    ft.app(target=main)