# modules/database.py
import sqlite3
import bcrypt

DB_FILENAME = "bonuza.db"


def get_connection():
    """Devuelve una conexión a la BD."""
    return sqlite3.connect(DB_FILENAME)


def init_db():
    """Crea tablas si no existen."""
    conn = get_connection()
    c = conn.cursor()
    # Tabla de usuarios
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        hash_pwd BLOB NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin','empleado'))
    )
    """)
    # Tabla de asistencia
    c.execute("""
    CREATE TABLE IF NOT EXISTS asistencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        ts_entrada TEXT NOT NULL,
        ts_salida TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)
    conn.commit()
    conn.close()


def create_default_admin():
    """Crea un admin por defecto si no existe."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios WHERE nombre='admin'")
    if c.fetchone()[0] == 0:
        pwd = "admin123".encode("utf-8")
        hash_pwd = bcrypt.hashpw(pwd, bcrypt.gensalt())
        c.execute(
            "INSERT INTO usuarios (nombre, hash_pwd, rol) VALUES (?,?,?)",
            ("admin", hash_pwd, "admin")
        )
        conn.commit()
    conn.close()
