import flet as ft
import os
from utils.excel_generator import ExcelGenerator

class ExcelGeneratorUI:
    def __init__(self, csv_data: list = None):
        self.csv_data = csv_data or []
        self.excel_generator = ExcelGenerator()
        self.output_folder = ""
        self.dieta_amount = 0.00
        
    def build(self):
        self.folder_picker = ft.FilePicker(
            on_result=self.on_folder_selected
        )
        
        # Campo de texto para ingresar manualmente la ruta
        self.folder_input = ft.TextField(
            label="Carpeta de destino",
            hint_text="/home/p102/Descargas",
            value="",
            width=400,
            on_change=self.on_folder_input_change
        )
        
        self.folder_text = ft.Text(
            "Ingresa la ruta de la carpeta de destino",
            color=ft.Colors.GREY_600
        )
        
        self.dieta_input = ft.TextField(
            label="Cantidad por dieta (€)",
            value="0.00",
            width=200,
            on_change=self.on_dieta_change
        )
        
        self.generate_button = ft.ElevatedButton(
            "Generar archivos Excel",
            icon=ft.Icons.DESCRIPTION,
            on_click=self.generate_excel_files,
            disabled=False
        )
        
        self.status_text = ft.Text(
            "",
            color=ft.Colors.GREEN,
            visible=False
        )
        
        self.error_text = ft.Text(
            "",
            color=ft.Colors.RED,
            visible=False
        )
        
        return ft.Column([
            self.folder_picker,
            ft.Text(
                "Generador de archivos Excel",
                size=16,
                weight=ft.FontWeight.BOLD
            ),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton(
                    "Explorar carpeta",
                    icon=ft.Icons.FOLDER,
                    on_click=self.on_folder_button_click
                ),
                ft.ElevatedButton(
                    "Usar Descargas",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=self.use_downloads_folder
                )
            ]),
            ft.Container(
                content=self.folder_input,
                padding=ft.padding.symmetric(vertical=10)
            ),
            self.folder_text,
            ft.Container(
                content=self.dieta_input,
                padding=ft.padding.all(10)
            ),
            ft.Container(
                content=self.generate_button,
                padding=ft.padding.all(10)
            ),
            self.status_text,
            self.error_text
        ])
    
    def use_downloads_folder(self, e):
        """Use the default Downloads folder"""
        downloads_path = os.path.expanduser("~/Descargas")
        if not os.path.exists(downloads_path):
            downloads_path = os.path.expanduser("~/Downloads")
        
        if os.path.exists(downloads_path):
            self.folder_input.value = downloads_path
            self.output_folder = downloads_path  # AGREGAR ESTA LÍNEA
            self.update_folder_from_input()
            if hasattr(self, 'page') and self.page:
                self.page.update()
        else:
            self.show_error("No se encontró la carpeta de Descargas")
    
    def on_folder_button_click(self, e):
        """Handle folder selection button click"""
        try:
            self.folder_picker.get_directory_path(dialog_title="Selecciona carpeta de destino")
        except Exception as ex:
            self.show_error("El selector de carpetas no está disponible en modo web. Ingresa la ruta manualmente.")
    
    def on_folder_selected(self, e: ft.FilePickerResultEvent):
        """Handle folder selection result"""
        if e.path:
            self.folder_input.value = e.path
            self.output_folder = e.path  # AGREGAR ESTA LÍNEA
            self.update_folder_from_input()
            if hasattr(self, 'page') and self.page:
                self.page.update()
    
    def on_folder_input_change(self, e):
        """Handle manual folder input change"""
        folder_path = e.control.value.strip()
        self.output_folder = folder_path  # AGREGAR ESTA LÍNEA
        self.update_folder_from_input()
    
    def update_folder_from_input(self):
        """Update folder state from input field value"""
        folder_path = self.folder_input.value.strip()
        
        if folder_path:
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                self.folder_text.value = f"✅ Carpeta válida: {folder_path}"
                self.folder_text.color = ft.Colors.GREEN
            else:
                self.folder_text.value = f"⚠️ Carpeta: {folder_path} (se creará si no existe)"
                self.folder_text.color = ft.Colors.ORANGE
        else:
            self.output_folder = ""
            self.folder_text.value = "Ingresa la ruta de la carpeta de destino"
            self.folder_text.color = ft.Colors.GREY_600
        
        self.update_generate_button_state()
        
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def on_dieta_change(self, e):
        try:
            self.dieta_amount = float(e.control.value.replace(',', '.'))
        except ValueError:
            self.dieta_amount = 0.00
        self.update_generate_button_state()
    
    def update_generate_button_state(self):
        """Update the state of the generate button"""
        has_folder = bool(self.output_folder.strip()) if self.output_folder else False
        has_data = bool(self.csv_data)
        
        print(f"Debug - Folder: '{self.output_folder}', Has folder: {has_folder}, Has data: {has_data}")
        
        # El botón SIEMPRE está activo
        self.generate_button.disabled = False
        
        # Update button text based on state
        if not has_data and not has_folder:
            self.generate_button.text = "Generar archivos Excel (sin datos ni carpeta)"
        elif not has_data:
            self.generate_button.text = "Generar archivos Excel (sin datos CSV)"
        elif not has_folder:
            self.generate_button.text = "Generar archivos Excel (sin carpeta)"
            print(f"Son carpeta pero {has_folder} y {has_data}")
        else:
            unique_employees = len(set(row['nombre'] for row in self.csv_data)) if self.csv_data else 0
            self.generate_button.text = f"Generar {unique_employees} archivos Excel"
        
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def generate_excel_files(self, e):
        try:
            self.hide_messages()
            
            if not self.csv_data:
                self.show_error("⚠️ No hay datos CSV cargados. Carga un archivo CSV primero.")
                return
            
            if not self.output_folder:
                self.show_error("⚠️ No hay carpeta de destino. Selecciona o escribe una carpeta.")
                return
            
            try:
                os.makedirs(self.output_folder, exist_ok=True)
            except Exception as ex:
                self.show_error(f"❌ No se pudo crear la carpeta: {str(ex)}")
                return
            
            generated_files = self.excel_generator.generate_excel_files(
                self.csv_data, 
                self.output_folder, 
                self.dieta_amount
            )
            
            if generated_files:
                self.show_status(f"✅ Se generaron {len(generated_files)} archivos Excel en: {self.output_folder}")
            else:
                self.show_error("❌ No se pudieron generar los archivos")
                
        except Exception as ex:
            self.show_error(f"❌ Error al generar archivos: {str(ex)}")
    
    def show_status(self, message: str):
        self.status_text.value = message
        self.status_text.visible = True
        self.error_text.visible = False
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def show_error(self, message: str):
        self.error_text.value = message
        self.error_text.visible = True
        self.status_text.visible = False
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def hide_messages(self):
        self.status_text.visible = False
        self.error_text.visible = False
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def set_csv_data(self, data: list):
        self.csv_data = data
        self.update_generate_button_state()
    
    def set_page(self, page):
        self.page = page