from sqlite3 import Row
from modules.database import get_connection

def create_table_empleados():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS empleados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        puesto TEXT,
        salario_semanal REAL NOT NULL,
        fecha_ingreso TEXT
    )""")
    conn.commit()
    conn.close()

def create_empleado(nombre: str, apellido: str, puesto: str, salario_semanal: float, fecha_ingreso: str) -> int:
    conn = get_connection(); c = conn.cursor()
    c.execute(
        "INSERT INTO empleados (nombre, apellido, puesto, salario_semanal, fecha_ingreso) VALUES (?,?,?,?,?)",
        (nombre, apellido, puesto, salario_semanal, fecha_ingreso)
    )
    conn.commit()
    emp_id = c.lastrowid
    conn.close()
    return emp_id

def get_empleados(limit: int = None) -> list[Row]:
    conn = get_connection(); conn.row_factory = Row; c = conn.cursor()
    q = "SELECT * FROM empleados ORDER BY id DESC"
    if limit: q += f" LIMIT {limit}"
    c.execute(q)
    rows = c.fetchall()
    conn.close()
    return rows

def update_empleado(emp_id: int, nombre: str, apellido: str, puesto: str, salario_semanal: float, fecha_ingreso: str) -> bool:
    conn = get_connection(); c = conn.cursor()
    c.execute("""
        UPDATE empleados
        SET nombre=?, apellido=?, puesto=?, salario_semanal=?, fecha_ingreso=?
        WHERE id=?
    """, (nombre, apellido, puesto, salario_semanal, fecha_ingreso, emp_id))
    conn.commit()
    changed = c.rowcount > 0
    conn.close()
    return changed

def delete_empleado(emp_id: int) -> bool:
    conn = get_connection(); c = conn.cursor()
    c.execute("DELETE FROM empleados WHERE id=?", (emp_id,))
    conn.commit()
    deleted = c.rowcount > 0
    conn.close()
    return deleted
