import { useAuth } from '../../../hooks/useAuth';
import { Button } from '../../ui/Button/Button';
import './Header.css';

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <div>
        <span className="header__eyebrow">Panel administrativo</span>
        <h1>Food Store</h1>
      </div>
      <div className="header__actions">
        <span className="header__user">{user?.name}</span>
        <Button variant="secondary" onClick={logout}>
          Cerrar sesion
        </Button>
      </div>
    </header>
  );
}
