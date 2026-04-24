from datetime import datetime
from app.database.connection import get_connection

def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()

def _normalize_age(value):
    if value is None:
        return None
    
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
        
    return int(value)

def list_characters(search_text=""):
    search_text = _clean_text(search_text)

    query = """
        SELECT id, nombre, raza, clase, edad, descripcion, created_at, updated_at
        FROM personajes
    """
    params = []

    if search_text:
        query += " WHERE nombre LIKE ? COLLATE NOCASE"
        params.append(f"%{search_text}%")

    query += " ORDER BY updated_at DESC, nombre COLLATE NOCASE ASC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    
    return [dict(row) for row in rows]

def get_character_by_id(character_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, nombre, raza, clase, edad, descripcion, created_at, updated_at
            FROM personajes
            WHERE id = ?
            """,
            (character_id,),
        ).fetchone()
    return dict(row) if row else None

def create_character(nombre, raza="", clase="", edad=None, descripcion=""):
    nombre = _clean_text(nombre)
    if not nombre:
        raise ValueError("El nombre no puede estar vacio.")
    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO personajes (
                nombre,
                raza,
                clase,
                edad,
                descripcion,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nombre,
                _clean_text(raza),
                _clean_text(clase),
                _normalize_age(edad),
                _clean_text(descripcion),
                now,
                now,
            ),
        )
        connection.commit()
    return cursor.lastrowid

def update_character(character_id, nombre, raza="", clase="", edad=None, descripcion=""):
    nombre = _clean_text(nombre)
    if not nombre:
        raise ValueError("El nombre no puede estar vacio.")
    
    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE personajes
            SET nombre = ?,
                raza = ?,
                clase = ?,
                edad = ?,
                descripcion = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                nombre,
                _clean_text(raza),
                _clean_text(clase),
                _normalize_age(edad),
                _clean_text(descripcion),
                now,
                character_id,
            ),
        )
        connection.commit()
    return cursor.rowcount > 0

def delete_character(character_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM personajes WHERE id = ?",
            (character_id,),
        )
        connection.commit()
    return cursor.rowcount > 0