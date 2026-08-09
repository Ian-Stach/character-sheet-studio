from datetime import datetime

from app.database.connection import get_connection


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def list_skills(search_text="", tipo=""):
    search_text = _clean_text(search_text)
    tipo = _clean_text(tipo)

    query = """
        SELECT id, nombre, tipo, descripcion, costo, notas, created_at, updated_at
        FROM habilidades
        WHERE 1=1
    """
    params = []

    if search_text:
        query += " AND nombre LIKE ? COLLATE NOCASE"
        params.append(f"%{search_text}%")

    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)

    query += " ORDER BY tipo ASC, nombre COLLATE NOCASE ASC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    return [dict(row) for row in rows]


def get_skill_by_id(skill_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, nombre, tipo, descripcion, costo, notas, created_at, updated_at
            FROM habilidades
            WHERE id = ?
            """,
            (skill_id,),
        ).fetchone()

    return dict(row) if row else None


def create_skill(nombre, tipo, descripcion="", costo="", notas=""):
    nombre = _clean_text(nombre)
    tipo = _clean_text(tipo)

    if not nombre:
        raise ValueError("El nombre no puede estar vacio.")
    if tipo not in ("activa", "pasiva"):
        raise ValueError("El tipo debe ser 'activa' o 'pasiva'.")

    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO habilidades (nombre, tipo, descripcion, costo, notas, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nombre,
                tipo,
                _clean_text(descripcion),
                _clean_text(costo),
                _clean_text(notas),
                now,
                now,
            ),
        )
        connection.commit()

    return cursor.lastrowid


def update_skill(skill_id, nombre, tipo, descripcion="", costo="", notas=""):
    nombre = _clean_text(nombre)
    tipo = _clean_text(tipo)

    if not nombre:
        raise ValueError("El nombre no puede estar vacio.")
    if tipo not in ("activa", "pasiva"):
        raise ValueError("El tipo debe ser 'activa' o 'pasiva'.")

    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE habilidades
            SET nombre = ?, tipo = ?, descripcion = ?, costo = ?, notas = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                nombre,
                tipo,
                _clean_text(descripcion),
                _clean_text(costo),
                _clean_text(notas),
                now,
                skill_id,
            ),
        )
        connection.commit()

    return cursor.rowcount > 0


def delete_skill(skill_id):
    with get_connection() as connection:
        try:
            cursor = connection.execute(
                "DELETE FROM habilidades WHERE id = ?",
                (skill_id,),
            )
            connection.commit()
        except Exception:
            return False

    return cursor.rowcount > 0


def get_character_skills(personaje_id):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT h.id, h.nombre, h.tipo, h.descripcion, h.costo, h.notas
            FROM habilidades h
            INNER JOIN personaje_habilidades ph ON ph.habilidad_id = h.id
            WHERE ph.personaje_id = ?
            ORDER BY h.tipo ASC, h.nombre COLLATE NOCASE ASC
            """,
            (personaje_id,),
        ).fetchall()

    return [dict(row) for row in rows]


def assign_skill_to_character(personaje_id, habilidad_id):
    with get_connection() as connection:
        try:
            connection.execute(
                """
                INSERT INTO personaje_habilidades (personaje_id, habilidad_id)
                VALUES (?, ?)
                """,
                (personaje_id, habilidad_id),
            )
            connection.commit()
        except Exception:
            return False

    return True


def remove_skill_from_character(personaje_id, habilidad_id):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM personaje_habilidades
            WHERE personaje_id = ? AND habilidad_id = ?
            """,
            (personaje_id, habilidad_id),
        )
        connection.commit()

    return cursor.rowcount > 0


def get_assigned_skill_ids(personaje_id):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT habilidad_id
            FROM personaje_habilidades
            WHERE personaje_id = ?
            """,
            (personaje_id,),
        ).fetchall()

    return {row["habilidad_id"] for row in rows}
