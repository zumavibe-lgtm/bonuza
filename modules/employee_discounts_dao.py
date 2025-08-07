# modules/employee_discounts_dao.py

from modules.database import get_connection

def create_table_discount_types():
    """Crea la tabla de tipos de descuento."""
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

def create_table_employee_discounts():
    """Crea la tabla de descuentos asignados a empleados."""
    conn = get_connection()
    c = conn.cursor()
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

def get_all_discount_types() -> list[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, nombre FROM discount_types ORDER BY nombre")
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'nombre': r[1]} for r in rows]

def add_discount_type(nombre: str) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO discount_types (nombre) VALUES (?)", (nombre,))
    conn.commit()
    dt_id = c.lastrowid
    conn.close()
    return dt_id

def get_employee_discounts(empleado_id: int) -> list[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT ed.id, dt.nombre, ed.valor, ed.es_porcentaje, ed.activo,
           ed.num_cuotas, ed.cuotas_restantes, ed.semana_inicio, ed.anio_inicio
      FROM employee_discounts ed
      JOIN discount_types dt ON ed.discount_type_id = dt.id
     WHERE ed.empleado_id = ?
     ORDER BY ed.id
    """, (empleado_id,))
    rows = c.fetchall()
    conn.close()
    cols = ['id','tipo','valor','es_porcentaje','activo',
            'num_cuotas','cuotas_restantes','semana_inicio','anio_inicio']
    return [dict(zip(cols, r)) for r in rows]

def add_employee_discount(discount_type_id: int, empleado_id: int,
                          valor: float, es_porcentaje: bool,
                          num_cuotas: int, semana_inicio: int,
                          anio_inicio: int) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO employee_discounts
      (discount_type_id, empleado_id, valor, es_porcentaje,
       activo, num_cuotas, cuotas_restantes, semana_inicio, anio_inicio)
    VALUES (?,?,?,?,?,?,?,?,?)
    """, (discount_type_id, empleado_id, valor,
          1 if es_porcentaje else 0,
          1,
          num_cuotas, num_cuotas,
          semana_inicio, anio_inicio))
    conn.commit()
    ed_id = c.lastrowid
    conn.close()
    return ed_id

def update_employee_discount(ed_id: int, valor: float, es_porcentaje: bool,
                             activo: bool, num_cuotas: int,
                             cuotas_restantes: int,
                             semana_inicio: int, anio_inicio: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    UPDATE employee_discounts
       SET valor=?, es_porcentaje=?, activo=?, num_cuotas=?,
           cuotas_restantes=?, semana_inicio=?, anio_inicio=?
     WHERE id=?
    """, (valor,
          1 if es_porcentaje else 0,
          1 if activo else 0,
          num_cuotas,
          cuotas_restantes,
          semana_inicio,
          anio_inicio,
          ed_id))
    conn.commit()
    changed = c.rowcount>0
    conn.close()
    return changed

def delete_employee_discount(ed_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM employee_discounts WHERE id=?", (ed_id,))
    conn.commit()
    deleted = c.rowcount>0
    conn.close()
    return deleted
