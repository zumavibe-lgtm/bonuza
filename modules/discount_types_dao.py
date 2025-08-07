# modules/discount_types_dao.py

from modules.database import get_connection

def create_table_discount_types():
    """
    Crea la tabla de tipos de descuento si no existe.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS discount_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def get_all_discount_types() -> list[dict]:
    """
    Devuelve todos los tipos de descuento registrados.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, nombre FROM discount_types ORDER BY nombre")
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'nombre': r[1]} for r in rows]

def add_discount_type(nombre: str) -> int:
    """
    Inserta un nuevo tipo de descuento y devuelve su ID.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO discount_types (nombre) VALUES (?)", (nombre,))
    conn.commit()
    dt_id = c.lastrowid
    conn.close()
    return dt_id
