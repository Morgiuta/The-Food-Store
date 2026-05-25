import { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { LogOut, Package, LayoutGrid, ShoppingCart, Users, Home, Menu, ChevronLeft, Utensils, ExternalLink } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export function AdminLayout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const menuItems = [
    { path: '/admin', icon: Home, label: 'Dashboard', roles: ['ADMIN', 'STOCK', 'PEDIDOS'] },
    { path: '/admin/categorias', icon: LayoutGrid, label: 'Categorías', roles: ['ADMIN', 'STOCK', 'PEDIDOS'] },
    { path: '/admin/ingredientes', icon: Utensils, label: 'Ingredientes', roles: ['ADMIN', 'STOCK'] },
    { path: '/admin/productos', icon: Package, label: 'Productos', roles: ['ADMIN', 'STOCK'] },
    { path: '/admin/pedidos', icon: ShoppingCart, label: 'Pedidos', roles: ['ADMIN', 'PEDIDOS'] },
    { path: '/admin/usuarios', icon: Users, label: 'Usuarios', roles: ['ADMIN'] },
  ];

  const filteredMenu = menuItems.filter(item => 
    !item.roles || item.roles.includes(user?.role || '')
  );

  return (
    <div className="min-h-screen flex bg-gray-50 overflow-hidden">
      {/* Sidebar */}
      <aside 
        className={`${isCollapsed ? 'w-20' : 'w-64'} bg-charcoal text-white flex flex-col transition-all duration-300 relative`}
      >
        <div className={`p-4 border-b border-gray-700 flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} h-20`}>
          {!isCollapsed && (
            <div>
              <h2 className="text-xl font-bold text-primary">Admin Panel</h2>
              <span className="inline-block mt-1 px-2 py-0.5 bg-gray-700 text-[10px] uppercase rounded-full">{user?.role}</span>
            </div>
          )}
          
          <button 
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-md hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
          >
            {isCollapsed ? <Menu size={24} /> : <ChevronLeft size={24} />}
          </button>
        </div>

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto overflow-x-hidden">
          {filteredMenu.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link 
                key={item.path}
                to={item.path} 
                title={isCollapsed ? item.label : undefined}
                className={`flex items-center gap-3 p-3 rounded-md transition-colors whitespace-nowrap
                  ${isActive ? 'bg-primary text-white font-medium' : 'text-gray-300 hover:bg-gray-800 hover:text-white'}`}
              >
                <Icon size={22} className="flex-shrink-0" /> 
                <span className={`transition-opacity duration-300 ${isCollapsed ? 'opacity-0 hidden' : 'opacity-100'}`}>
                  {item.label}
                </span>
              </Link>
            );
          })}
        </nav>

        <div className="p-3 border-t border-gray-700">
          <button 
            onClick={handleLogout}
            title={isCollapsed ? "Cerrar Sesión" : undefined}
            className="flex items-center gap-3 p-3 w-full rounded-md hover:bg-red-900/50 transition-colors text-red-400"
          >
            <LogOut size={22} className="flex-shrink-0" /> 
            {!isCollapsed && <span>Cerrar Sesión</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto h-screen bg-gray-50 flex flex-col">
        <header className="h-20 bg-white border-b border-gray-200 flex items-center px-8 shadow-sm shrink-0">
          <div className="flex-1"></div>
          <div className="flex items-center gap-6">
             <a 
               href={import.meta.env.VITE_STORE_URL || 'http://localhost:5174'} 
               target="_blank" 
               rel="noopener noreferrer"
               className="flex items-center gap-2 text-sm font-bold text-gray-500 hover:text-primary transition-colors"
             >
               <ExternalLink size={18} />
               Ver tienda
             </a>
             <div className="flex items-center gap-3 border-l border-gray-200 pl-6">
               <div className="text-right">
                  <p className="text-sm font-bold text-gray-800">{user?.name || user?.nombre}</p>
               </div>
               <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">
                 {user?.name?.charAt(0).toUpperCase() || user?.nombre?.charAt(0).toUpperCase() || 'A'}
               </div>
             </div>
          </div>
        </header>
        <div className="p-8 flex-1">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
