from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from app.database.character_repository import delete_character, list_characters
from app.ui.character_form import CharacterForm

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biblioteca de personajes")
        self.resize(900, 600)

        self.characters = []
        self.selected_character_id = None

        self._build_ui()
        self.load_characters()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        title_label = QLabel("Biblioteca de personajes")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        main_layout.addWidget(title_label)

        search_layout = QHBoxLayout()
        main_layout.addLayout(search_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre...")
        self.search_input.textChanged.connect(self.load_characters)
        search_layout.addWidget(self.search_input)

        clear_button = QPushButton("Limpiar")
        clear_button.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_button)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Nombre", "Raza", "Clase", "Edad", "Modificado"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.open_character)
        main_layout.addWidget(self.table)

        self.empty_state_label = QLabel("No hay personajes creados todavia.")
        self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state_label.setStyleSheet("font-size: 16px; color: gray; padding: 16px;")
        main_layout.addWidget(self.empty_state_label)

        footer_layout = QHBoxLayout()
        main_layout.addLayout(footer_layout)

        self.status_label = QLabel("0 personajes")
        footer_layout.addWidget(self.status_label)

        footer_layout.addStretch()

        self.new_button = QPushButton("Nuevo")
        self.new_button.clicked.connect(self.new_character)
        footer_layout.addWidget(self.new_button)

        self.open_button = QPushButton("Abrir")
        self.open_button.clicked.connect(self.open_character)
        self.open_button.setEnabled(False)
        footer_layout.addWidget(self.open_button)

        self.delete_button = QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_selected_character)
        self.delete_button.setEnabled(False)
        footer_layout.addWidget(self.delete_button)

    def load_characters(self, select_character_id=None):
        search_text = self.search_input.text()
        self.characters = list_characters(search_text)
        self.selected_character_id = None

        self.table.setRowCount(len(self.characters))

        for row_index, character in enumerate(self.characters):
            self.table.setItem(row_index, 0, QTableWidgetItem(character["nombre"]))
            self.table.setItem(row_index, 1, QTableWidgetItem(character["raza"] or ""))
            self.table.setItem(row_index, 2, QTableWidgetItem(character["clase"] or ""))
            age_value = "" if character["edad"] is None else str(character["edad"])
            self.table.setItem(row_index, 3, QTableWidgetItem(age_value))

            try:
                updated_dt = datetime.fromisoformat(character["updated_at"])
                updated_text = updated_dt.strftime("%d/%m/%Y %H:%M")
            except (ValueError, TypeError):
                updated_text = character["updated_at"] or ""
            self.table.setItem(row_index, 4, QTableWidgetItem(updated_text))
        
        self.table.setVisible(bool(self.characters))
        self.empty_state_label.setVisible(not self.characters)

        if self.characters:
            self.status_label.setText(f"{len(self.characters)} personajes")
        else:
            if search_text.strip():
                self.empty_state_label.setText("No se encontraron personajes.")
            else:
                self.empty_state_label.setText("No hay personajes creados todavia.")
            self.status_label.setText("0 personajes")
        
        self.open_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.table.resizeColumnsToContents()

        if select_character_id is not None:
            for row_index, character in enumerate(self.characters):
                if character["id"] == select_character_id:
                    self.table.selectRow(row_index)
                    break

    def clear_search(self):
        self.search_input.clear()
    
    def on_selection_changed(self):
        selected_row = self.table.currentRow()
        if selected_row < 0 or selected_row >= len(self.characters):
            self.selected_character_id = None
            self.open_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return
        
        self.selected_character_id = self.characters[selected_row]["id"]
        self.open_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def new_character(self):
        dialog = CharacterForm(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_characters(select_character_id=dialog.saved_character_id)

    def open_character(self):
        if self.selected_character_id is None:
            return

        try:
            dialog = CharacterForm(self, character_id=self.selected_character_id)
        except ValueError as error:
            QMessageBox.warning(self, "Error", str(error))
            self.load_characters()
            return
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_characters(select_character_id=dialog.saved_character_id)
    
    def delete_selected_character(self):
        if self.selected_character_id is None:
            return
        
        reply = QMessageBox.question(
            self,
            "Eliminar personaje",
            "¿Seguro que quieres eliminar este personaje?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        deleted = delete_character(self.selected_character_id)

        if not deleted:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo eliminar el personaje seleccionado.",
            )
            return
        self.load_characters()