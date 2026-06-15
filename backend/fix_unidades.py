from sqlalchemy import select
from app.core.database import get_session
from app.modules.unidad_medida.models import UnidadMedida
from app.modules.producto.models import Producto
from app.modules.producto_ingrediente.models import ProductoIngrediente
from app.modules.ingrediente.models import Ingrediente

def main():
    session = next(get_session())
    try:
        # Get 'un' unit
        stmt_un = select(UnidadMedida).where(UnidadMedida.codigo == 'un')
        un_res = session.execute(stmt_un)
        un_unit = un_res.scalar_one_or_none()
        
        # Get 'ud' unit
        stmt_ud = select(UnidadMedida).where(UnidadMedida.codigo == 'ud')
        ud_res = session.execute(stmt_ud)
        ud_unit = ud_res.scalar_one_or_none()
        
        if not ud_unit:
            print("Unit 'ud' not found.")
            return
        
        if not un_unit:
            print("Unit 'un' not found. Cannot merge.")
            return
            
        print(f"Found 'un' (ID: {un_unit.id}) and 'ud' (ID: {ud_unit.id}). Merging...")
        
        # Update Productos
        stmt_prod = select(Producto).where(Producto.unidad_venta_id == ud_unit.id)
        prods = session.execute(stmt_prod).scalars().all()
        for p in prods:
            p.unidad_venta_id = un_unit.id
            print(f"Updated Producto ID: {p.id}")
            
        # Update Ingredientes
        stmt_ing = select(Ingrediente).where(Ingrediente.unidad_medida_id == ud_unit.id)
        ings = session.execute(stmt_ing).scalars().all()
        for i in ings:
            i.unidad_medida_id = un_unit.id
            print(f"Updated Ingrediente ID: {i.id}")
            
        # Update ProductoIngrediente
        stmt_pi = select(ProductoIngrediente).where(ProductoIngrediente.unidad_medida_id == ud_unit.id)
        pis = session.execute(stmt_pi).scalars().all()
        for pi in pis:
            pi.unidad_medida_id = un_unit.id
            print(f"Updated ProductoIngrediente {pi.producto_id}-{pi.ingrediente_id}")
            
        session.flush()
        
        # Delete the 'ud' unit
        print("Deleting 'ud' unit...")
        session.delete(ud_unit)
        session.commit()
        print("Done!")
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()
        
if __name__ == "__main__":
    main()
