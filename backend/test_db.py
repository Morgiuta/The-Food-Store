import sys
sys.path.append('.')
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    res = conn.execute(text('SELECT p.id, p.estado_codigo, p.forma_pago_codigo, p.total FROM pedidos p ORDER BY p.id DESC LIMIT 5;')).fetchall()
    for row in res:
        print(row)
