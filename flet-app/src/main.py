import flet as ft
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.csv_view import CSVView

def main(page: ft.Page):
    page.title = "Nova Dietas - CSV Selector"
    page.window_width = 1200
    page.window_height = 800
    page.padding = 20
    
    # Create and add the CSV view
    csv_view = CSVView()
    csv_view.set_page(page)
    page.add(csv_view.build())

if __name__ == "__main__":
    ft.app(target=main)