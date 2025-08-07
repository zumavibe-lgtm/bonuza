# modules/ptu_dao.py

import sqlite3
from datetime import datetime, date
from modules.database import get_connection

def create_table_ptu_config():
    """
    Configuración de PTU:
      - monto_total REAL
      - porcentaje REAL (sobre salario anual)
      - dias_minimos INTEGER (mínimo laborado para ser elegible)
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS ptu_config (
        id INTEGER PRIMARY KEY CHECK(id=1),
        monto_total REAL NOT NULL,
        porcentaje REAL NOT NULL,
        dias_minimos INTEGER NOT NULL
    )
    """)
    # valores por defecto
    c.execute("INSERT OR IGNORE INTO ptu_config (id, monto_total, porcentaje, dias_minimos) VALUES (1, 0, 0, 0)")
    conn.commit()
    conn.close()

def get_ptu_config() -> dict:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT monto_total, porcentaje, dias_minimos FROM ptu_config WHERE id=1")
    row = c.fetchone()
    conn.close()
    return {'monto_total': row[0], 'porcentaje': row[1], 'dias_minimos': row[2]}

def set_ptu_config(monto_total: float, porcentaje: float, dias_minimos: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE ptu_config
           SET monto_total=?, porcentaje=?, dias_minimos=?
         WHERE id=1
    """, (monto_total, porcentaje, dias_minimos))
    conn.commit()
    conn.close()

def calculate_ptu(hasta_fecha: str) -> list[dict]:
    """
    Calcula la PTU para cada empleado elegible hasta 'hasta_fecha' (YYYY-MM-DD).
    Retorna lista de dicts por empleado con:
      id, nombre, dias_trabajados, salario_anual, ptu_individual
    """
    conn = get_connection()
    c = conn.cursor()

    # cargar config
    config = get_ptu_config()
    monto_total = config['monto_total']
    pct = config['porcentaje'] / 100.0
    dias_min = config['dias_minimos']

    # obtener todos los empleados y su ingreso y salario
    c.execute("SELECT id, nombre, apellido, fecha_ingreso, salario_semanal FROM empleados")
    empleados = c.fetchall()

    resultados = []
    for emp_id, nombre, apellido, f_ingreso, sal_sem in empleados:
        # calcular días trabajados
        f0 = datetime.fromisoformat(f_ingreso).date()
        fh = datetime.fromisoformat(hasta_fecha).date()
        dias = (fh - f0).days + 1
        if dias < dias_min:
            continue

        salario_anual = sal_sem * 52  # 52 semanas
        participacion = salario_anual * pct
        resultados.append({
            'empleado_id': emp_id,
            'empleado': f"{nombre} {apellido}",
            'dias_trabajados': dias,
            'salario_anual': round(salario_anual,2),
            'ptu_individual': round(participacion,2)
        })

    # normalizar a proporción del monto_total
    total_part = sum(r['ptu_individual'] for r in resultados)
    if total_part > 0:
        factor = monto_total / total_part
        for r in resultados:
            r['ptu_individual'] = round(r['ptu_individual'] * factor,2)

    conn.close()
    return resultados
