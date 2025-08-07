# modules/database.py

import sqlite3
import bcrypt

DB_FILENAME = "bonuza.db"

def get_connection():
    """Devuelve una conexión a la base de datos."""
    return sqlite3.connect(DB_FILENAME)

def init_db():
    """Crea todas las tablas principales si no existen."""
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

    # Tabla de empleados
    c.execute("""
    CREATE TABLE IF NOT EXISTS empleados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        puesto TEXT,
        salario_semanal REAL NOT NULL,
        fecha_ingreso TEXT
    )
    """)

    # Tabla de configuración global
    c.execute("""
    CREATE TABLE IF NOT EXISTS config (
        clave TEXT PRIMARY KEY,
        valor TEXT NOT NULL
    )
    """)

    # Tabla de descuentos de ley (porcentaje)
    c.execute("""
    CREATE TABLE IF NOT EXISTS descuentos (
        clave TEXT PRIMARY KEY,
        valor REAL NOT NULL
    )
    """)

    # Tabla de nómina
    c.execute("""
    CREATE TABLE IF NOT EXISTS nomina (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT NOT NULL,
        horas_trabajadas REAL NOT NULL DEFAULT 0.0,
        sueldo_bruto REAL NOT NULL DEFAULT 0.0,
        descuentos_total REAL NOT NULL DEFAULT 0.0,
        neto_a_pagar REAL NOT NULL DEFAULT 0.0,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)

    # Tipos de descuento dinámicos
    c.execute("""
    CREATE TABLE IF NOT EXISTS discount_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL
    )
    """)

    # Descuentos asignados por empleado
    c.execute("""
    CREATE TABLE IF NOT EXISTS employee_discounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discount_type_id INTEGER NOT NULL,
        empleado_id       INTEGER NOT NULL,
        valor             REAL    NOT NULL,
        es_porcentaje     INTEGER  NOT NULL CHECK(es_porcentaje IN (0,1)),
        activo            INTEGER  NOT NULL CHECK(activo IN (0,1)),
        num_cuotas        INTEGER  DEFAULT NULL,
        cuotas_restantes  INTEGER  DEFAULT NULL,
        semana_inicio     INTEGER  NOT NULL,
        anio_inicio       INTEGER  NOT NULL,
        FOREIGN KEY(discount_type_id) REFERENCES discount_types(id),
        FOREIGN KEY(empleado_id)       REFERENCES empleados(id)
    )
    """)

    conn.commit()
    conn.close()

def create_default_admin():
    """Inserta un administrador por defecto si no existe."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios WHERE nombre='admin'")
    if c.fetchone()[0] == 0:
        pwd = b"admin123"
        hash_pwd = bcrypt.hashpw(pwd, bcrypt.gensalt())
        c.execute(
            "INSERT INTO usuarios (nombre, hash_pwd, rol) VALUES (?,?,?)",
            ("admin", hash_pwd, "admin")
        )
        conn.commit()
    conn.close()

if __name__ == "__main__":
    # Solo al ejecutar este módulo directamente se inicializan los DAOs auxiliares
    init_db()
    create_default_admin()

    from .empleados_dao              import create_table_empleados
    from .config_dao                 import create_table_config
    from .descuentos_dao             import create_table_descuentos
    from .nomina_dao                 import create_table_nomina
    from .discount_types_dao         import create_table_discount_types
    from .employee_discounts_dao     import create_table_employee_discounts

    create_table_empleados()
    create_table_config()
    create_table_descuentos()
    create_table_nomina()
    create_table_discount_types()
    create_table_employee_discounts()
