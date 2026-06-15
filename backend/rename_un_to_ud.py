from sqlalchemy import select
from app.core.database import get_session
from app.modules.unidad_medida.models import UnidadMedida

def main():
    session = next(get_session())
    try:
        stmt_un = select(UnidadMedida).where(UnidadMedida.codigo == 'un')
        un_res = session.execute(stmt_un)
        un_unit = un_res.scalar_one_or_none()
        
        if not un_unit:
            print("Unit 'un' not found.")
            return
            
        print(f"Renaming 'un' (ID: {un_unit.id}) to 'ud'...")
        un_unit.codigo = 'ud'
        un_unit.nombre = 'Unidad'
        un_unit.simbolo = 'ud'
        
        session.commit()
        print("Done!")
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()
        
if __name__ == "__main__":
    main()
