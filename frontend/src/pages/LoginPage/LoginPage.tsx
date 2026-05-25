import { FormEvent, useState, useEffect } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import type { LoginCredentials } from '../../types/auth';
import { useAuthStore } from '../../store/authStore';
import { getErrorMessage } from '../../utils/errors';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, login, user } = useAuthStore();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [credentials, setCredentials] = useState<LoginCredentials>({
    username: '',
    password: '',
  });

  const from = location.state?.from?.pathname ?? '/admin';
  const mensaje = location.state?.mensaje;
  const [showBanner, setShowBanner] = useState(!!mensaje);

  useEffect(() => {
    if (showBanner) {
      const timer = setTimeout(() => setShowBanner(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [showBanner]);

  if (isAuthenticated) {
    return <Navigate to={user?.role === 'CLIENT' ? '/' : '/admin'} replace />;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(credentials);
      const currentUser = useAuthStore.getState().user;
      navigate(currentUser?.role === 'CLIENT' && from === '/admin' ? '/' : from, { replace: true });
    } catch (loginError: unknown) {
      setError(getErrorMessage(loginError, 'No se pudo iniciar sesión.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-bg flex items-center justify-center p-4">
      <section className="bg-surface w-full max-w-md rounded-lg shadow-soft p-8">
        <div className="flex items-center gap-4 mb-8">
          <span className="bg-primary text-white font-bold text-2xl h-12 w-12 flex items-center justify-center rounded-lg">FS</span>
          <div>
            <h1 className="text-xl font-bold leading-tight">Food Store</h1>
            <p className="text-sm text-muted">Gestión de hamburguesería</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <span className="section-kicker">Acceso interno</span>
            <h2 className="text-2xl font-bold mt-1">Ingresar al panel</h2>
            <p className="text-sm text-muted mt-1">Credenciales por defecto: admin@admin.com / admin123</p>
          </div>

          {showBanner && (
            <div className="p-3 bg-green-100 text-green-800 text-sm font-medium rounded-md">
              {mensaje}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-charcoal mb-1">Email de Usuario</label>
              <input
                className="w-full p-3 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                name="username"
                placeholder="admin@admin.com"
                value={credentials.username}
                autoComplete="username"
                onChange={(event) => {
                  setCredentials((current) => ({ ...current, username: event.target.value }));
                  setShowBanner(false);
                }}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-charcoal mb-1">Contraseña</label>
              <input
                className="w-full p-3 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                name="password"
                placeholder="****"
                type="password"
                value={credentials.password}
                autoComplete="current-password"
                onChange={(event) => {
                  setCredentials((current) => ({ ...current, password: event.target.value }));
                  setShowBanner(false);
                }}
              />
            </div>
          </div>

          {error && <div className="p-3 bg-red-100 text-red-700 text-sm rounded-md">{error}</div>}

          <button 
            type="submit" 
            disabled={isSubmitting}
            className="w-full bg-primary hover:bg-primary-dark text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Validando...' : 'Entrar'}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-muted">
          Queres comprar online?{' '}
          <a href="/registro" className="font-bold text-primary-dark hover:underline">
            Crear cuenta
          </a>
        </p>
      </section>
    </main>
  );
}
