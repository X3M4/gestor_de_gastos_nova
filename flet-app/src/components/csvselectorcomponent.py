import flet as ft
import csv
from typing import List, Dict, Callable

class CSVSelectorComponent:
    def __init__(self, on_file_loaded: Callable[[List[Dict]], None] = None):
        self.on_file_loaded = on_file_loaded
        self.data = []
        self.file_picker = None
        self.file_name_text = None
        self.data_table = None
        self.error_text = None
        
    def build(self):
        self.file_picker = ft.FilePicker(
            on_result=self.on_file_selected
        )
        
        self.file_name_text = ft.Text(
            "No hay archivo seleccionado",
            color=ft.Colors.GREY_600
        )
        
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Proyecto")),
                ft.DataColumn(ft.Text("Fecha")),
            ],
            rows=[],
            visible=False
        )
        
        self.error_text = ft.Text(
            "",
            color=ft.Colors.RED,
            visible=False
        )
        
        return ft.Column([
            self.file_picker,
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        "Seleccionar archivo CSV",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda _: self.file_picker.pick_files(
                            allow_multiple=False,
                            allowed_extensions=["csv"]
                        )
                    ),
                    self.file_name_text
                ]),
                padding=ft.padding.all(10)
            ),
            self.error_text,
            ft.Container(
                content=self.data_table,
                padding=ft.padding.all(10)
            )
        ])
    
    def on_file_selected(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            self.file_name_text.value = e.files[0].name
            self.load_csv_data(file_path)
            if hasattr(self, 'page') and self.page:
                self.page.update()
    
    def load_csv_data(self, file_path: str):
        try:
            self.data = []
            self.data_table.rows.clear()
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                # Verify headers
                expected_headers = ['nombre', 'proyecto', 'fecha']
                if not all(header in csv_reader.fieldnames for header in expected_headers):
                    self.show_error("El archivo CSV debe tener las columnas: nombre, proyecto, fecha")
                    return
                
                # Load data
                for row in csv_reader:
                    self.data.append({
                        'nombre': row['nombre'],
                        'proyecto': row['proyecto'],
                        'fecha': row['fecha']
                    })
                    
                    self.data_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(row['nombre'])),
                            ft.DataCell(ft.Text(row['proyecto'][:50] + "..." if len(row['proyecto']) > 50 else row['proyecto'])),
                            ft.DataCell(ft.Text(row['fecha']))
                        ])
                    )
                
                self.data_table.visible = True
                self.error_text.visible = False
                
                # Notify parent component
                if self.on_file_loaded:
                    self.on_file_loaded(self.data)
                    
        except Exception as ex:
            self.show_error(f"Error al cargar el archivo: {str(ex)}")
    
    def show_error(self, message: str):
        self.error_text.value = message
        self.error_text.visible = True
        self.data_table.visible = False
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def set_page(self, page):
        self.page = page