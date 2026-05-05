import { FormEvent, useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button/Button';
import { Input } from '../../components/ui/Input/Input';
import { useAuth } from '../../hooks/useAuth';
import type { LoginCredentials } from '../../types/auth';
import './LoginPage.css';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, login } = useAuth();
  const [credentials, setCredentials] = useState<LoginCredentials>({
    username: '',
    password: '',
  });

  const from = location.state?.from?.pathname ?? '/';

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    login(credentials);
    navigate(from, { replace: true });
  };

  return (
    <main className="login-page">
      <section className="login-page__panel">
        <div className="login-page__brand">
          <span className="login-page__logo">FS</span>
          <div>
            <span>Food Store</span>
            <strong>Gestion de hamburgueseria</strong>
          </div>
        </div>

        <form className="login-page__form" onSubmit={handleSubmit}>
          <div>
            <span className="section-kicker">Acceso interno</span>
            <h1>Ingresar al panel</h1>
            <p>Login mock para primera entrega funcional.</p>
          </div>

          <Input
            label="Usuario"
            name="username"
            placeholder="admin"
            value={credentials.username}
            onChange={(event) =>
              setCredentials((current) => ({ ...current, username: event.target.value }))
            }
          />

          <Input
            label="Contrasena"
            name="password"
            placeholder="1234"
            type="password"
            value={credentials.password}
            onChange={(event) =>
              setCredentials((current) => ({ ...current, password: event.target.value }))
            }
          />

          <Button type="submit">Entrar</Button>
        </form>
      </section>
    </main>
  );
}
