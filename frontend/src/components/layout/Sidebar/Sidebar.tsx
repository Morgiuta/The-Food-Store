import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const menuItems = [
  { to: '/', label: 'Home', end: true },
  { to: '/insumos', label: 'Insumos' },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <aside className={`sidebar ${isOpen ? 'sidebar--open' : ''}`} aria-hidden={!isOpen}>
      <div className="sidebar__brand">
        <div className="sidebar__brand-main">
          <span className="sidebar__logo">FS</span>
          <div>
            <strong>Food Store</strong>
            <small>Burger admin</small>
          </div>
        </div>
        <button
          className="sidebar__menu-button"
          type="button"
          aria-label="Cerrar menu"
          onClick={onClose}
          tabIndex={isOpen ? undefined : -1}
        >
          <span />
          <span />
          <span />
        </button>
      </div>
      <nav className="sidebar__nav" aria-label="Menu principal">
        {menuItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              isActive ? 'sidebar__link sidebar__link--active' : 'sidebar__link'
            }
            onClick={onClose}
            tabIndex={isOpen ? undefined : -1}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
