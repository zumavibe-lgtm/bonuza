# modules/config_dao.py
from modules.database import get_connection

CONFIG_KEYS = ['hora_entrada', 'hora_salida', 'tolerancia_minutos']

def create_table_config():
    """Crea la tabla config si no existe e inserta valores por defecto."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS config (
        clave TEXT PRIMARY KEY,
        valor TEXT NOT NULL
    )
    """)
    # Valores por defecto
    for clave, valor in [
        ('hora_entrada', '09:00'),
        ('hora_salida',  '18:00'),
        ('tolerancia_minutos', '5')
    ]:
        c.execute("INSERT OR IGNORE INTO config (clave, valor) VALUES (?,?)",
                  (clave, valor))
    conn.commit()
    conn.close()

def get_config():
    """Retorna un dict {clave: valor} con la configuración."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT clave, valor FROM config")
    rows = c.fetchall()
    conn.close()
    return {clave: valor for clave, valor in rows}

def set_config(clave: str, valor: str):
    """Actualiza un valor existente en config."""
    if clave not in CONFIG_KEYS:
        raise KeyError(f"Clave inválida: {clave}")
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE config SET valor=? WHERE clave=?", (valor, clave))
    conn.commit()
    conn.close()
