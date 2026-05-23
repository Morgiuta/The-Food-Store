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
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [credentials, setCredentials] = useState<LoginCredentials>({
    username: '',
    password: '',
  });

  const from = location.state?.from?.pathname ?? '/';

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(credentials);
      navigate(from, { replace: true });
    } catch (loginError) {
      setError(
        loginError instanceof Error
          ? loginError.message
          : 'No se pudo iniciar sesion.',
      );
    } finally {
      setIsSubmitting(false);
    }
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
            <p>Credenciales demo: admin/1234 o stock/stock.</p>
          </div>

          <Input
            label="Usuario"
            name="username"
            placeholder="admin"
            value={credentials.username}
            autoComplete="username"
            onChange={(event) =>
              setCredentials((current) => ({ ...current, username: event.target.value }))
            }
          />

          <Input
            label="Contraseña"
            name="password"
            placeholder="1234"
            type="password"
            value={credentials.password}
            autoComplete="current-password"
            onChange={(event) =>
              setCredentials((current) => ({ ...current, password: event.target.value }))
            }
          />

          {error ? <div className="login-page__error">{error}</div> : null}

          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Validando...' : 'Entrar'}
          </Button>
        </form>
      </section>
    </main>
  );
}
