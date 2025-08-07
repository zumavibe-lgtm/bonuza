# modules/nomina_dao.py

from modules.database import get_connection
from datetime import datetime
from modules.descuentos_dao import get_descuentos, DISCOUNT_KEYS

def create_table_nomina():
    """Crea la tabla nomina si no existe."""
    conn = get_connection()
    c = conn.cursor()
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
    conn.commit()
    conn.close()

def calcular_nomina(usuario_id: int, fecha_inicio: str, fecha_fin: str) -> dict:
    """
    Calcula y guarda nómina para un usuario en un rango:
    - Suma horas de asistencia
    - Calcula sueldo bruto
    - Aplica descuentos porcentuales
    - Guarda y retorna un dict con todos los totales
    """
    # Convertir strings ISO a datetime
    dt_inicio = datetime.fromisoformat(fecha_inicio)
    dt_fin    = datetime.fromisoformat(fecha_fin)
    if dt_fin < dt_inicio:
        raise ValueError("Fecha fin debe ser ≥ fecha inicio")

    conn = get_connection()
    c = conn.cursor()

    # 1. Sumar horas trabajadas
    c.execute("""
        SELECT ts_entrada, ts_salida
          FROM asistencia
         WHERE usuario_id=?
           AND ts_entrada >= ?
           AND ts_entrada <= ?
    """, (usuario_id, fecha_inicio, fecha_fin))
    total_horas = 0.0
    for ent, sal in c.fetchall():
        d_ent = datetime.fromisoformat(ent)
        d_sal = datetime.fromisoformat(sal) if sal else dt_fin
        delta = d_sal - d_ent
        total_horas += delta.total_seconds() / 3600

    # 2. Calcular tarifa por hora y sueldo bruto
    c.execute("SELECT salario_semanal FROM empleados WHERE id=?", (usuario_id,))
    row = c.fetchone()
    tarifa = 0.0
    if row:
        salario_sem = row[0]
        tarifa = (salario_sem / 6) / 8
    sueldo_bruto = total_horas * tarifa

    # 3. Cargar descuentos (%) y calcular total
    descuentos_cfg = get_descuentos()
    total_pct = sum(descuentos_cfg.get(k, 0.0) for k in DISCOUNT_KEYS)
    descuentos = sueldo_bruto * total_pct / 100

    # 4. Calcular neto
    neto = sueldo_bruto - descuentos

    # 5. Guardar en BD
    c.execute("""
        INSERT INTO nomina
        (usuario_id, fecha_inicio, fecha_fin, horas_trabajadas,
         sueldo_bruto, descuentos_total, neto_a_pagar)
        VALUES (?,?,?,?,?,?,?)
    """, (
        usuario_id, fecha_inicio, fecha_fin, total_horas,
        sueldo_bruto, descuentos, neto
    ))
    conn.commit()
    nomina_id = c.lastrowid
    conn.close()

    return {
        'id': nomina_id,
        'usuario_id': usuario_id,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'horas_trabajadas': round(total_horas, 2),
        'sueldo_bruto': round(sueldo_bruto, 2),
        'descuentos_total': round(descuentos, 2),
        'neto_a_pagar': round(neto, 2)
    }

def get_nominas(usuario_id: int = None) -> list[dict]:
    """Devuelve lista de nóminas, opcionalmente filtrada por usuario."""
    conn = get_connection()
    c = conn.cursor()
    if usuario_id:
        c.execute("SELECT * FROM nomina WHERE usuario_id=? ORDER BY fecha_inicio DESC", (usuario_id,))
    else:
        c.execute("SELECT * FROM nomina ORDER BY fecha_inicio DESC")
    rows = c.fetchall()
    conn.close()
    cols = ['id','usuario_id','fecha_inicio','fecha_fin',
            'horas_trabajadas','sueldo_bruto','descuentos_total','neto_a_pagar']
    return [dict(zip(cols, r)) for r in rows]

def get_nomina_by_id(nomina_id: int) -> dict | None:
    """Devuelve dict de una nómina por su ID o None."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM nomina WHERE id=?", (nomina_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    cols = ['id','usuario_id','fecha_inicio','fecha_fin',
            'horas_trabajadas','sueldo_bruto','descuentos_total','neto_a_pagar']
    return dict(zip(cols, row))
