import { FormEvent, useState, useEffect } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { getErrorMessage } from '../../utils/errors';
import { useMutation } from '@tanstack/react-query';
import { authService } from '../../services/authService';

export function RegisterPage() {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuthStore();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    nombre: '',
    apellido: '',
    celular: '',
    email: '',
    password: '',
  });

  // Limpiar cualquier token o sesión existente
  useEffect(() => {
    logout();
  }, [logout]);

  const registerMutation = useMutation({
    mutationFn: () => authService.register(form),
    onSuccess: () => {
      navigate('/login', { state: { mensaje: '¡Cuenta creada! Iniciá sesión para continuar.' } });
    },
    onError: (err) => {
      setError(getErrorMessage(err, 'No se pudo crear la cuenta.'));
    }
  });

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    registerMutation.mutate();
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-bg p-4">
      <section className="w-full max-w-md rounded-lg bg-surface p-8 shadow-soft">
        <div className="mb-8 flex items-center gap-4">
          <span className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-2xl font-bold text-white">
            FS
          </span>
          <div>
            <h1 className="text-xl font-bold leading-tight">Crear cuenta</h1>
            <p className="text-sm text-muted">Compra online en Food Store</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-bold text-charcoal">Nombre</label>
              <input
                className="w-full rounded-md border border-border p-3 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-primary"
                value={form.nombre}
                onChange={(event) => setForm((current) => ({ ...current, nombre: event.target.value }))}
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-bold text-charcoal">Apellido</label>
              <input
                className="w-full rounded-md border border-border p-3 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-primary"
                value={form.apellido}
                onChange={(event) => setForm((current) => ({ ...current, apellido: event.target.value }))}
                required
              />
            </div>
          </div>
          
          <div>
            <label className="mb-1 block text-sm font-bold text-charcoal">
              Celular <span className="font-medium text-muted">(Opcional)</span>
            </label>
            <input
              className="w-full rounded-md border border-border p-3 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-primary"
              type="tel"
              value={form.celular}
              onChange={(event) => setForm((current) => ({ ...current, celular: event.target.value }))}
              placeholder="Ej: 1123456789"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-bold text-charcoal">Email</label>
            <input
              className="w-full rounded-md border border-border p-3 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-primary"
              type="email"
              value={form.email}
              onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-bold text-charcoal">Contraseña</label>
            <input
              className="w-full rounded-md border border-border p-3 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-primary"
              type="password"
              value={form.password}
              onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
              required
            />
          </div>

          {error && <div className="rounded-md bg-red-100 p-3 text-sm text-red-700">{error}</div>}

          <button
            type="submit"
            disabled={registerMutation.isPending}
            className="w-full rounded-md bg-primary px-4 py-3 font-black text-white transition-colors hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-70"
          >
            {registerMutation.isPending ? 'Creando...' : 'Registrarme'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Ya tenes cuenta?{' '}
          <Link to="/login" className="font-bold text-primary-dark hover:underline">
            Ingresar
          </Link>
        </p>
      </section>
    </main>
  );
}
