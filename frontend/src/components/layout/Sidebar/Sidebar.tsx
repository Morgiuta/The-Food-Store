import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const menuItems = [
  { to: '/', label: 'Home', end: true },
  { to: '/insumos', label: 'Insumos' },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__logo">FS</span>
        <div>
          <strong>Food Store</strong>
          <small>Burger admin</small>
        </div>
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
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
