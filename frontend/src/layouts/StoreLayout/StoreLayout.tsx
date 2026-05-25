import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import { LogOut, Menu, ShoppingCart, UserRound } from 'lucide-react';
import { useCartStore } from '../../store/cartStore';
import { useAuthStore } from '../../store/authStore';

export function StoreLayout() {
  const navigate = useNavigate();
  const itemsCount = useCartStore((state) =>
    state.items.reduce((total, item) => total + item.cantidad, 0),
  );
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-bg">
      <header className="sticky top-0 z-20 border-b border-border bg-surface/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
          <Link to="/" className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-md bg-primary text-lg font-black text-white">
              FS
            </span>
            <div>
              <p className="text-base font-black leading-tight">Food Store</p>
              <p className="text-xs font-semibold text-muted">Hamburgueseria</p>
            </div>
          </Link>

          <nav className="hidden items-center gap-2 text-sm font-bold md:flex">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `rounded-md px-3 py-2 ${isActive ? 'bg-surface-warm text-primary-dark' : 'text-charcoal hover:bg-surface-warm'}`
              }
            >
              Catalogo
            </NavLink>
            <NavLink
              to="/mis-pedidos"
              className={({ isActive }) =>
                `rounded-md px-3 py-2 ${isActive ? 'bg-surface-warm text-primary-dark' : 'text-charcoal hover:bg-surface-warm'}`
              }
            >
              Mis pedidos
            </NavLink>
            <NavLink
              to="/direcciones"
              className={({ isActive }) =>
                `rounded-md px-3 py-2 ${isActive ? 'bg-surface-warm text-primary-dark' : 'text-charcoal hover:bg-surface-warm'}`
              }
            >
              Direcciones
            </NavLink>
            {user?.role === 'ADMIN' && (
              <NavLink to="/admin" className="rounded-md px-3 py-2 text-charcoal hover:bg-surface-warm">
                Admin
              </NavLink>
            )}
          </nav>

          <div className="flex items-center gap-2">
            <Link
              to="/carrito"
              className="relative inline-flex h-10 w-10 items-center justify-center rounded-md border border-border bg-surface text-charcoal hover:border-primary"
              title="Carrito"
            >
              <ShoppingCart size={20} />
              {itemsCount > 0 && (
                <span className="absolute -right-2 -top-2 min-w-5 rounded-full bg-ketchup px-1.5 text-center text-xs font-black text-white">
                  {itemsCount}
                </span>
              )}
            </Link>

            {isAuthenticated && user ? (
              <button
                type="button"
                onClick={handleLogout}
                className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-surface px-3 text-sm font-bold text-charcoal hover:border-primary"
              >
                <LogOut size={17} />
                <span className="hidden sm:inline">{user.name}</span>
              </button>
            ) : (
              <Link
                to="/login"
                className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-3 text-sm font-black text-white hover:bg-primary-dark"
              >
                <UserRound size={17} />
                Ingresar
              </Link>
            )}

            <button
              type="button"
              className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-border md:hidden"
              title="Menu"
            >
              <Menu size={20} />
            </button>
          </div>
        </div>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  );
}
