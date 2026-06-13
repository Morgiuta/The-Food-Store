from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.modules.auth.models import Rol, Usuario, UsuarioRol
from app.modules.unidad_medida.models import UnidadMedida
from app.modules.ventas.models import EstadoPedido, FormaPago


DEFAULT_ADMIN_EMAIL = "admin@foodstore.com"
DEFAULT_ADMIN_PASSWORD = "Admin1234!"


ROLES_SEED = [
    ("ADMIN", "Administrador", "CRUD completo de todo el sistema"),
    ("CLIENT", "Cliente", "Catalogo, carrito y pedidos propios"),
    ("STOCK", "Gestor de Stock", "Lectura de productos y gestion de stock"),
    ("PEDIDOS", "Gestor de Pedidos", "Visualizacion y avance de estados de pedidos"),
]

ESTADOS_PEDIDO_SEED = [
    ("PENDIENTE", "Pendiente", 1, False),
    ("CONFIRMADO", "Confirmado", 2, False),
    ("EN_PREP", "En preparacion", 3, False),
    ("ENTREGADO", "Entregado", 4, True),
    ("CANCELADO", "Cancelado", 5, True),
]

FORMAS_PAGO_SEED = [
    ("MERCADOPAGO", "MercadoPago", True),
    ("EFECTIVO", "Efectivo", True),
    ("TRANSFERENCIA", "Transferencia", True),
]

UNIDADES_MEDIDA_SEED = [
    ("kg", "Kilogramo", "kg"),
    ("g", "Gramo", "g"),
    ("L", "Litro", "L"),
    ("ml", "Mililitro", "ml"),
    ("ud", "Unidad", "ud"),
    ("porciones", "Porciones", "porciones"),
]


def seed_required_data(session: Session) -> None:
    seed_roles(session)
    seed_estados_pedido(session)
    seed_formas_pago(session)
    seed_unidades_medida(session)
    seed_default_admin(session)
    session.commit()


def seed_roles(session: Session) -> None:
    for codigo, nombre, descripcion in ROLES_SEED:
        if session.get(Rol, codigo) is None:
            session.add(Rol(codigo=codigo, nombre=nombre, descripcion=descripcion))


def seed_estados_pedido(session: Session) -> None:
    for codigo, descripcion, orden, es_terminal in ESTADOS_PEDIDO_SEED:
        estado = session.get(EstadoPedido, codigo)
        if estado is None:
            session.add(
                EstadoPedido(
                    codigo=codigo,
                    descripcion=descripcion,
                    orden=orden,
                    es_terminal=es_terminal,
                )
            )
        else:
            estado.descripcion = descripcion
            estado.orden = orden
            estado.es_terminal = es_terminal
            session.add(estado)


def seed_formas_pago(session: Session) -> None:
    for codigo, descripcion, habilitado in FORMAS_PAGO_SEED:
        forma_pago = session.get(FormaPago, codigo)
        if forma_pago is None:
            session.add(
                FormaPago(
                    codigo=codigo,
                    descripcion=descripcion,
                    habilitado=habilitado,
                )
            )
        else:
            forma_pago.descripcion = descripcion
            forma_pago.habilitado = habilitado
            session.add(forma_pago)

    legacy_tarjeta = session.get(FormaPago, "TARJETA")
    if legacy_tarjeta is not None:
        legacy_tarjeta.habilitado = False
        session.add(legacy_tarjeta)


def seed_unidades_medida(session: Session) -> None:
    for codigo, nombre, simbolo in UNIDADES_MEDIDA_SEED:
        unidad = session.exec(
            select(UnidadMedida).where(UnidadMedida.codigo == codigo)
        ).first()
        if unidad is None:
            session.add(
                UnidadMedida(
                    codigo=codigo,
                    nombre=nombre,
                    simbolo=simbolo,
                )
            )
        else:
            unidad.nombre = nombre
            unidad.simbolo = simbolo
            unidad.deleted_at = None
            session.add(unidad)


def seed_default_admin(session: Session) -> None:
    email = DEFAULT_ADMIN_EMAIL.lower()
    admin = session.exec(select(Usuario).where(Usuario.email == email)).first()

    if admin is None:
        admin = Usuario(
            nombre="Admin",
            apellido="Default",
            email=email,
            password_hash=get_password_hash(DEFAULT_ADMIN_PASSWORD),
        )
        session.add(admin)
        session.flush()

    if admin.id is None:
        return

    admin_role = session.get(UsuarioRol, (admin.id, "ADMIN"))
    if admin_role is None:
        session.add(UsuarioRol(usuario_id=admin.id, rol_codigo="ADMIN"))
