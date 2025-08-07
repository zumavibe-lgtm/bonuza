# modules/vacaciones_dao.py

import sqlite3
from datetime import datetime, date, timedelta
from modules.database import get_connection

def create_table_vacaciones():
    """
    Crea la tabla de vacaciones:
      - id
      - empleado_id
      - fecha_inicio (ISO date)
      - fecha_fin   (ISO date)
      - dias_totales
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS vacaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado_id INTEGER NOT NULL,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT NOT NULL,
        dias_totales REAL NOT NULL,
        FOREIGN KEY(empleado_id) REFERENCES empleados(id)
    )
    """)
    conn.commit()
    conn.close()

def add_vacaciones(empleado_id: int, fecha_inicio: str, fecha_fin: str) -> int:
    """
    Inserta un periodo de vacaciones para un empleado.
    fecha_inicio/fecha_fin en "YYYY-MM-DD".
    Calcula dias_totales como diferencia + 1.
    Devuelve el id recién creado.
    """
    d0 = datetime.fromisoformat(fecha_inicio).date()
    d1 = datetime.fromisoformat(fecha_fin).date()
    if d1 < d0:
        raise ValueError("Fecha fin debe ser ≥ fecha inicio")
    dias = (d1 - d0).days + 1

    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO vacaciones (empleado_id, fecha_inicio, fecha_fin, dias_totales)
    VALUES (?,?,?,?)
    """, (empleado_id, fecha_inicio, fecha_fin, dias))
    conn.commit()
    vid = c.lastrowid
    conn.close()
    return vid

def get_vacaciones(empleado_id: int = None) -> list[dict]:
    """
    Devuelve todos los registros de vacaciones, o filtrados por empleado.
    """
    conn = get_connection()
    c = conn.cursor()
    if empleado_id:
        c.execute("""
        SELECT v.id, v.empleado_id, e.nombre || ' ' || e.apellido AS empleado,
               v.fecha_inicio, v.fecha_fin, v.dias_totales
          FROM vacaciones v
          JOIN empleados e ON v.empleado_id = e.id
         WHERE v.empleado_id=?
         ORDER BY v.fecha_inicio DESC
        """, (empleado_id,))
    else:
        c.execute("""
        SELECT v.id, v.empleado_id, e.nombre || ' ' || e.apellido AS empleado,
               v.fecha_inicio, v.fecha_fin, v.dias_totales
          FROM vacaciones v
          JOIN empleados e ON v.empleado_id = e.id
         ORDER BY v.fecha_inicio DESC
        """)
    rows = c.fetchall()
    conn.close()
    cols = ['id','empleado_id','empleado','fecha_inicio','fecha_fin','dias_totales']
    return [dict(zip(cols, r)) for r in rows]

def delete_vacaciones(vac_id: int) -> bool:
    """
    Elimina un registro de vacaciones. Devuelve True si existía.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM vacaciones WHERE id=?", (vac_id,))
    conn.commit()
    ok = c.rowcount > 0
    conn.close()
    return ok
