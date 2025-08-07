# modules/aguinaldo_dao.py

import sqlite3
from datetime import datetime, date
from modules.database import get_connection

def create_table_aguinaldo():
    """
    Crea la tabla de parámetros de aguinaldo (días otorgados).
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS aguinaldo_config (
        id INTEGER PRIMARY KEY CHECK(id=1),
        dias_otorgados REAL NOT NULL
    )
    """)
    # Inserta configuración por defecto si no existe
    c.execute("INSERT OR IGNORE INTO aguinaldo_config (id, dias_otorgados) VALUES (1, 15)")
    conn.commit()
    conn.close()

def get_aguinaldo_days() -> float:
    """
    Obtiene los días de aguinaldo configurados.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT dias_otorgados FROM aguinaldo_config WHERE id=1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0.0

def set_aguinaldo_days(dias: float):
    """
    Actualiza los días de aguinaldo.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE aguinaldo_config SET dias_otorgados=? WHERE id=1", (dias,))
    conn.commit()
    conn.close()

def calculate_aguinaldo_for_employee(empleado_id: int, hasta_fecha: str) -> dict:
    """
    Calcula el monto de aguinaldo proporcional al tiempo laborado hasta 'hasta_fecha' (YYYY-MM-DD).
    Retorna dict con {'empleado_id', 'dias_trabajados', 'dias_config', 'sueldo_diario', 'monto_aguinaldo'}.
    """
    conn = get_connection()
    c = conn.cursor()

    # 1) Obtener fecha de ingreso y salario semanal
    c.execute("SELECT fecha_ingreso, salario_semanal FROM empleados WHERE id=?", (empleado_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise ValueError("Empleado no encontrado")
    fecha_ingreso, salario_sem = row
    # convertir fechas
    f_ing = datetime.fromisoformat(fecha_ingreso).date()
    f_hasta = datetime.fromisoformat(hasta_fecha).date()
    if f_hasta < f_ing:
        conn.close()
        raise ValueError("Fecha hasta anterior a ingreso")

    # 2) Calcular días trabajados (sin incluir futuros)
    dias_trab = (f_hasta - f_ing).days + 1

    # 3) Cálculo de sueldo diario
    sueldo_diario = (salario_sem / 6)

    # 4) Obtener días de aguinaldo configurados
    dias_cfg = get_aguinaldo_days()

    # 5) Proporción de aguinaldo
    # Aguinaldo = sueldo_diario * dias_cfg * (dias_trab / 365)
    monto = sueldo_diario * dias_cfg * (dias_trab / 365)

    conn.close()
    return {
        'empleado_id': empleado_id,
        'dias_trabajados': dias_trab,
        'dias_config': dias_cfg,
        'sueldo_diario': round(sueldo_diario,2),
        'monto_aguinaldo': round(monto,2)
    }
