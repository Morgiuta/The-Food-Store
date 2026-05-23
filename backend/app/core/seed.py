from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.modules.auth.models import Rol, Usuario, UsuarioRol
from app.modules.ventas.models import EstadoPedido, FormaPago


DEFAULT_ADMIN_EMAIL = "admin@admin.com"
DEFAULT_ADMIN_PASSWORD = "admin123"


ROLES_SEED = [
    ("ADMIN", "Administrador", "CRUD completo de todo el sistema"),
    ("CLIENT", "Cliente", "Catalogo, carrito y pedidos propios"),
    ("STOCK", "Gestor de Stock", "Lectura de productos y gestion de stock"),
    ("PEDIDOS", "Gestor de Pedidos", "Visualizacion y avance de estados de pedidos"),
]

ESTADOS_PEDIDO_SEED = [
    ("PENDIENTE", "Pendiente", 1, False),
    ("CONFIRMADO", "Confirmado", 2, False),
    ("EN_PROCESO", "En proceso", 3, False),
    ("LISTO", "Listo", 4, False),
    ("ENTREGADO", "Entregado", 5, True),
    ("CANCELADO", "Cancelado", 6, True),
]

FORMAS_PAGO_SEED = [
    ("EFECTIVO", "Efectivo", True),
    ("TARJETA", "Tarjeta", True),
]


def seed_required_data(session: Session) -> None:
    seed_roles(session)
    seed_estados_pedido(session)
    seed_formas_pago(session)
    seed_default_admin(session)
    session.commit()


def seed_roles(session: Session) -> None:
    for codigo, nombre, descripcion in ROLES_SEED:
        if session.get(Rol, codigo) is None:
            session.add(Rol(codigo=codigo, nombre=nombre, descripcion=descripcion))


def seed_estados_pedido(session: Session) -> None:
    for codigo, descripcion, orden, es_terminal in ESTADOS_PEDIDO_SEED:
        if session.get(EstadoPedido, codigo) is None:
            session.add(
                EstadoPedido(
                    codigo=codigo,
                    descripcion=descripcion,
                    orden=orden,
                    es_terminal=es_terminal,
                )
            )


def seed_formas_pago(session: Session) -> None:
    for codigo, descripcion, habilitado in FORMAS_PAGO_SEED:
        if session.get(FormaPago, codigo) is None:
            session.add(
                FormaPago(
                    codigo=codigo,
                    descripcion=descripcion,
                    habilitado=habilitado,
                )
            )


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
