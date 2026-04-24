from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)
from app.database.character_repository import (
    create_character,
    get_character_by_id,
    update_character,
)

class CharacterForm(QDialog):
    def __init__(self, parent=None, character_id=None):
        super().__init__(parent)
        self.character_id = character_id
        self.saved_character_id = None
        self.character_data = (
            get_character_by_id(character_id) if character_id is not None else None
        )

        if character_id is not None and self.character_data is None:
            raise ValueError(f"No existe el personaje con id {character_id}.")
        
        self.setWindowTitle(
            "Nuevo personaje" if self.character_data is None else "Editar personaje"
        )
        self.resize(500, 420)

        self._build_ui()

        if self.character_data is not None:
            self._load_character_data()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        self.nombre_input = QLineEdit()
        form_layout.addRow("Nombre:", self.nombre_input)

        self.raza_input = QLineEdit()
        form_layout.addRow("Raza:", self.raza_input)

        self.clase_input = QLineEdit()
        form_layout.addRow("Clase / Rol:", self.clase_input)

        self.edad_input = QLineEdit()
        self.edad_input.setPlaceholderText("Dejar vacio si no aplica")
        form_layout.addRow("Edad:", self.edad_input)

        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción breve del personaje...")
        self.descripcion_input.setFixedHeight(120)
        form_layout.addRow("Descripcion:", self.descripcion_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.save_character)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    
    def _load_character_data(self):
        self.nombre_input.setText(self.character_data["nombre"] or "")
        self.raza_input.setText(self.character_data["raza"] or "")
        self.clase_input.setText(self.character_data["clase"] or "")
        
        edad = self.character_data["edad"]
        self.edad_input.setText("" if edad is None else str(edad))

        self.descripcion_input.setPlainText(self.character_data["descripcion"] or "")
    
    def _get_age_value(self):
        age_text = self.edad_input.text().strip()
        if not age_text:
            return None
        try:
            age_value = int(age_text)

        except ValueError as error:
            raise ValueError("La edad debe ser un numero entero.") from error
        
        if age_value < 0:
            raise ValueError("La edad no puede ser negativa.")
        
        return age_value

    def save_character(self):
        nombre = self.nombre_input.text().strip()
        raza = self.raza_input.text().strip()
        clase = self.clase_input.text().strip()
        descripcion = self.descripcion_input.toPlainText().strip()

        if not nombre:
            QMessageBox.warning(self, "Validacion", "El nombre es obligatorio.")
            self.nombre_input.setFocus()
            return

        try:
            edad = self._get_age_value()

            if self.character_id is None:
                self.saved_character_id = create_character(
                    nombre,
                    raza,
                    clase,
                    edad,
                    descripcion,
                )
            else:
                updated = update_character(
                    self.character_id,
                    nombre,
                    raza,
                    clase,
                    edad,
                    descripcion,
                )
                if not updated:
                    raise ValueError("No se pudo actualizar el personaje.")
                self.saved_character_id = self.character_id
        
        except ValueError as error:
            QMessageBox.warning(self, "Validacion", str(error))
            return
        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"Ocurrio un error al guardar el personaje:\n{error}",
            )
            return
        self.accept()