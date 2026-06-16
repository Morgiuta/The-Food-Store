import { useState, useEffect, useRef } from 'react';
import { Link, NavLink, Outlet, useNavigate, useSearchParams } from 'react-router-dom';
import { LogOut, Menu, ShoppingCart, UserCircle, Package, MapPin, Search } from 'lucide-react';
import { useCartStore } from '../../store/cartStore';
import { useAuthStore } from '../../store/authStore';

export function StoreLayout() {
  const navigate = useNavigate();
  const itemsCount = useCartStore((state) =>
    state.items.reduce((total, item) => total + item.cantidad, 0),
  );
  const { user, isAuthenticated, logout } = useAuthStore();
  
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const search = searchParams.get('q') || '';

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-bg">
      <header className="sticky top-0 z-20 border-b border-border bg-surface/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-y-3 gap-x-4 px-4 py-3">
          <Link to="/" className="flex items-center gap-3 shrink-0">
            <span className="flex h-10 w-10 items-center justify-center rounded-md bg-primary text-lg font-black text-white">
              FS
            </span>
            <div>
              <p className="text-base font-black leading-tight">Food Store</p>
              <p className="text-xs font-semibold text-muted">Hamburgueseria</p>
            </div>
          </Link>

          <div className="flex w-full order-3 md:order-2 md:w-auto md:flex-1 items-center md:mx-10">
            <div className="flex w-full items-center gap-2 rounded-md border border-border bg-white px-3 py-2 transition-colors focus-within:border-primary focus-within:ring-1 focus-within:ring-primary/20 shadow-sm">
              <Search size={18} className="text-muted shrink-0" />
              <input
                className="w-full bg-transparent text-sm font-semibold outline-none text-charcoal"
                placeholder="Buscar hamburguesas, bebidas, combos..."
                value={search}
                onChange={(event) => {
                  const newQ = event.target.value;
                  if (newQ) {
                    setSearchParams(prev => { prev.set('q', newQ); return prev; });
                  } else {
                    setSearchParams(prev => { prev.delete('q'); return prev; });
                  }
                }}
              />
            </div>

            {user?.role === 'ADMIN' && (
              <NavLink to="/admin" className="ml-4 shrink-0 whitespace-nowrap rounded-md px-3 py-2 text-sm font-bold text-charcoal hover:bg-surface-warm">
                Admin
              </NavLink>
            )}
          </div>

          <div className="flex items-center gap-2 order-2 md:order-3 shrink-0">
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
              <div className="relative" ref={dropdownRef}>
                <button
                  type="button"
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-border bg-surface text-charcoal hover:border-primary"
                  title="Perfil"
                >
                  <UserCircle size={20} />
                </button>

                {isDropdownOpen && (
                  <div className="absolute right-0 top-full mt-2 w-56 rounded-md border border-border bg-white shadow-lg z-50">
                    <div className="border-b border-border px-4 py-3">
                      <p className="text-sm font-bold text-charcoal">{user.name}</p>
                    </div>
                    <div className="py-1">
                      <Link
                        to="/mis-pedidos"
                        onClick={() => setIsDropdownOpen(false)}
                        className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-charcoal hover:bg-surface-warm"
                      >
                        <Package size={16} /> Mis pedidos
                      </Link>
                      <Link
                        to="/mis-direcciones"
                        onClick={() => setIsDropdownOpen(false)}
                        className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-charcoal hover:bg-surface-warm"
                      >
                        <MapPin size={16} /> Mis direcciones
                      </Link>
                    </div>
                    <div className="border-t border-border py-1">
                      <button
                        type="button"
                        onClick={() => {
                          setIsDropdownOpen(false);
                          handleLogout();
                        }}
                        className="flex w-full items-center gap-2 px-4 py-2 text-sm font-semibold text-ketchup hover:bg-red-50"
                      >
                        <LogOut size={16} /> Cerrar sesión
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-3 text-sm font-black text-white hover:bg-primary-dark"
              >
                <UserCircle size={17} />
                Ingresar
              </Link>
            )}

          </div>
        </div>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  );
}
