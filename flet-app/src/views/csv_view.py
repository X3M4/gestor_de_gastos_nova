import flet as ft
from components.csvselectorcomponent import CSVSelectorComponent
from components.excel_generator_component import ExcelGeneratorUI

class CSVView:
    def __init__(self):
        self.loaded_data = []
        self.csv_selector = None
        self.excel_generator_ui = None
        self.stats_text = None
        self.page = None
        
    def build(self):
        self.csv_selector = CSVSelectorComponent(
            on_file_loaded=self.on_csv_loaded
        )
        
        self.excel_generator_ui = ExcelGeneratorUI()
        
        self.stats_text = ft.Text(
            "",
            size=16,
            weight=ft.FontWeight.BOLD,
            visible=False
        )
        
        # Componentes en paralelo (lado a lado)
        return ft.Column([
            ft.Text(
                "Nova Dietas - Generador de Excel",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Divider(),
            self.stats_text,
            ft.Row([
                # Columna izquierda - Selector CSV
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "1. Seleccionar archivo CSV",
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        self.csv_selector.build()
                    ]),
                    width=600,
                    padding=ft.padding.all(10)
                ),
                # Separador vertical
                ft.VerticalDivider(),
                # Columna derecha - Generador Excel
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "2. Generar archivos Excel",
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        self.excel_generator_ui.build()
                    ]),
                    width=600,
                    padding=ft.padding.all(10)
                )
            ], 
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START)
        ], scroll=ft.ScrollMode.AUTO)
    
    def on_csv_loaded(self, data):
        self.loaded_data = data
        unique_names = len(set(row['nombre'] for row in data))
        unique_projects = len(set(row['proyecto'] for row in data))
        
        self.stats_text.value = f"✅ Datos cargados: {len(data)} registros, {unique_names} personas, {unique_projects} proyectos"
        self.stats_text.visible = True
        self.stats_text.color = "#4CAF50"
        
        # Update Excel generator with new data
        if self.excel_generator_ui:
            self.excel_generator_ui.set_csv_data(data)
        
        if self.page:
            self.page.update()
    
    def set_page(self, page):
        self.page = page
        if self.csv_selector:
            self.csv_selector.set_page(page)
        if self.excel_generator_ui:
            self.excel_generator_ui.set_page(page)