import { FormEvent, useState } from 'react';
import { Home, Star, Trash2 } from 'lucide-react';
import { useDirecciones } from '../../hooks/useDirecciones';
import type { DireccionFormValues } from '../../types/direccion';
import { getErrorMessage } from '../../utils/errors';

const emptyForm: DireccionFormValues = {
  alias: '',
  calle: '',
  numero: '',
  ciudad: '',
  provincia: '',
  codigo_postal: '',
  es_principal: false,
};

export function AddressesPage() {
  const {
    direcciones,
    isLoading,
    error,
    isMutating,
    createDireccion,
    markPrincipal,
    deleteDireccion,
  } = useDirecciones();
  const [form, setForm] = useState<DireccionFormValues>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);

    try {
      await createDireccion(form);
      setForm(emptyForm);
    } catch (createError: unknown) {
      setFormError(getErrorMessage(createError, 'No se pudo guardar.'));
    }
  };

  return (
    <section className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6">
        <span className="section-kicker">Cuenta</span>
        <h1 className="mt-1 text-3xl font-black">Direcciones de entrega</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        <form onSubmit={handleSubmit} className="h-fit rounded-lg border border-border bg-surface p-5">
          <h2 className="mb-4 text-lg font-black">Agregar direccion</h2>
          <div className="space-y-3">
            <input
              className="w-full rounded-md border border-border p-3 outline-none focus:ring-2 focus:ring-primary"
              placeholder="Alias: Casa, Trabajo"
              value={form.alias}
              onChange={(event) => setForm((current) => ({ ...current, alias: event.target.value }))}
            />
            <div className="grid grid-cols-[1fr_110px] gap-3">
              <input
                className="w-full rounded-md border border-border p-3 outline-none focus:ring-2 focus:ring-primary"
                placeholder="Calle"
                value={form.calle}
                onChange={(event) => setForm((current) => ({ ...current, calle: event.target.value }))}
                required
              />
              <input
                className="w-full rounded-md border border-border p-3 outline-none focus:ring-2 focus:ring-primary"
                placeholder="Numero"
                value={form.numero}
                onChange={(event) => setForm((current) => ({ ...current, numero: event.target.value }))}
                required
              />
            </div>
            <input
              className="w-full rounded-md border border-border p-3 outline-none focus:ring-2 focus:ring-primary"
              placeholder="Ciudad"
              value={form.ciudad}
              onChange={(event) => setForm((current) => ({ ...current, ciudad: event.target.value }))}
              required
            />
            <div className="grid grid-cols-2 gap-3">
              <input
                className="w-full rounded-md border border-border p-3 outline-none focus:ring-2 focus:ring-primary"
                placeholder="Provincia"
                value={form.provincia}
                onChange={(event) => setForm((current) => ({ ...current, provincia: event.target.value }))}
              />
              <input
                className="w-full rounded-md border border-border p-3 outline-none focus:ring-2 focus:ring-primary"
                placeholder="CP"
                value={form.codigo_postal}
                onChange={(event) =>
                  setForm((current) => ({ ...current, codigo_postal: event.target.value }))
                }
              />
            </div>
            <label className="flex items-center gap-2 text-sm font-bold text-muted">
              <input
                type="checkbox"
                checked={form.es_principal}
                onChange={(event) =>
                  setForm((current) => ({ ...current, es_principal: event.target.checked }))
                }
              />
              Marcar como principal
            </label>
          </div>

          {formError && <div className="mt-4 rounded-md bg-red-100 p-3 text-sm text-red-700">{formError}</div>}

          <button
            type="submit"
            disabled={isMutating}
            className="mt-5 w-full rounded-md bg-primary px-4 py-3 font-black text-white hover:bg-primary-dark disabled:opacity-70"
          >
            Guardar direccion
          </button>
        </form>

        <div className="space-y-3">
          {error && <div className="rounded-md bg-red-100 p-3 text-sm text-red-700">{error}</div>}
          {isLoading ? (
            <div className="rounded-lg border border-border bg-surface p-8 text-center font-bold text-muted">
              Cargando direcciones...
            </div>
          ) : direcciones.length === 0 ? (
            <div className="rounded-lg border border-border bg-surface p-8 text-center font-bold text-muted">
              No tenes direcciones guardadas.
            </div>
          ) : (
            direcciones.map((direccion) => (
              <article key={direccion.id} className="rounded-lg border border-border bg-surface p-5">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <Home size={18} className="text-primary-dark" />
                      <h2 className="text-lg font-black">{direccion.alias || 'Direccion'}</h2>
                      {direccion.es_principal && (
                        <span className="rounded-md bg-lettuce px-2 py-1 text-xs font-black text-white">
                          Principal
                        </span>
                      )}
                    </div>
                    <p className="mt-2 font-semibold text-muted">
                      {direccion.calle} {direccion.numero}, {direccion.ciudad}
                    </p>
                    <p className="text-sm font-semibold text-muted">
                      {[direccion.provincia, direccion.codigo_postal].filter(Boolean).join(' - ')}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    {!direccion.es_principal && (
                      <button
                        type="button"
                        onClick={() => markPrincipal(direccion.id)}
                        className="inline-flex h-10 items-center gap-2 rounded-md border border-border px-3 text-sm font-black hover:border-primary"
                      >
                        <Star size={16} />
                        Principal
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => deleteDireccion(direccion.id)}
                      className="inline-flex h-10 items-center gap-2 rounded-md border border-border px-3 text-sm font-black text-ketchup hover:border-ketchup"
                    >
                      <Trash2 size={16} />
                      Eliminar
                    </button>
                  </div>
                </div>
              </article>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
