import { FormEvent, useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { getErrorMessage } from '../../utils/errors';

export function RegisterPage() {
  const navigate = useNavigate();
  const { isAuthenticated, register } = useAuthStore();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [form, setForm] = useState({
    nombre: '',
    email: '',
    password: '',
  });

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await register(form);
      navigate('/checkout', { replace: true });
    } catch (registerError: unknown) {
      setError(getErrorMessage(registerError, 'No se pudo crear la cuenta.'));
    } finally {
      setIsSubmitting(false);
    }
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
          <div>
            <label className="mb-1 block text-sm font-bold text-charcoal">Nombre completo</label>
            <input
              className="w-full rounded-md border border-border p-3 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-primary"
              value={form.nombre}
              onChange={(event) => setForm((current) => ({ ...current, nombre: event.target.value }))}
              required
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
            <label className="mb-1 block text-sm font-bold text-charcoal">Contrasena</label>
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
            disabled={isSubmitting}
            className="w-full rounded-md bg-primary px-4 py-3 font-black text-white transition-colors hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? 'Creando...' : 'Registrarme'}
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
