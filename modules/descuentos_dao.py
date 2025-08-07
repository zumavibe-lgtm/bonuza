# modules/descuentos_dao.py

from modules.database import get_connection

# Claves de descuentos porcentuales
DISCOUNT_KEYS = ['IMSS', 'INFONAVIT', 'ISR', 'AFORE']

def create_table_descuentos():
    """
    Crea la tabla descuentos si no existe y carga valores por defecto (0.0).
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS descuentos (
        clave TEXT PRIMARY KEY,
        valor REAL NOT NULL
    )
    """)
    # Inserta cada clave con valor 0.0 si no existe
    for clave in DISCOUNT_KEYS:
        c.execute(
            "INSERT OR IGNORE INTO descuentos (clave, valor) VALUES (?,?)",
            (clave, 0.0)
        )
    conn.commit()
    conn.close()

def get_descuentos() -> dict:
    """
    Devuelve un dict {clave: valor} con los descuentos porcentuales actuales.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT clave, valor FROM descuentos")
    rows = c.fetchall()
    conn.close()
    return {clave: valor for clave, valor in rows}

def set_descuento(clave: str, valor: float):
    """
    Actualiza el valor de un descuento porcentual.
    """
    if clave not in DISCOUNT_KEYS:
        raise KeyError(f"Clave inválida: {clave}")
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE descuentos SET valor=? WHERE clave=?",
        (valor, clave)
    )
    conn.commit()
    conn.close()
