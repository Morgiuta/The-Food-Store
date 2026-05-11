import { useAuth } from '../../../hooks/useAuth';
import { Button } from '../../ui/Button/Button';
import './Header.css';

interface HeaderProps {
  isSidebarOpen: boolean;
  onMenuToggle: () => void;
}

export function Header({ isSidebarOpen, onMenuToggle }: HeaderProps) {
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <div className="header__title-group">
        {!isSidebarOpen ? (
          <button
            className="header__menu-button"
            type="button"
            aria-label="Abrir menu"
            onClick={onMenuToggle}
          >
            <span />
            <span />
            <span />
          </button>
        ) : null}
        <div>
          <span className="header__eyebrow">Panel administrativo</span>
          <h1>Food Store</h1>
        </div>
      </div>
      <div className="header__actions">
        <span className="header__user">
          {user?.name} - {user?.role}
        </span>
        <Button variant="secondary" onClick={logout}>
          Cerrar sesion
        </Button>
      </div>
    </header>
  );
}
