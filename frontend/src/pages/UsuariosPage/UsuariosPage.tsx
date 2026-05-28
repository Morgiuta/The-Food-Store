import { useMemo, useState } from 'react';
import { Modal } from '../../components/ui/Modal/Modal';
import { useToast } from '../../components/ui/Toast/Toast';
import { UsuarioFormModal } from '../../features/usuarios/components/UsuarioFormModal/UsuarioFormModal';
import { UsuariosTable } from '../../features/usuarios/components/UsuariosTable/UsuariosTable';
import { useUsuarios } from '../../hooks/useUsuarios';
import type { UsuariosQuery, UsuarioPublic, UsuarioUpdate } from '../../types/usuario';

const defaultQuery: UsuariosQuery = {
  page: 1,
  limit: 20,
};

export function UsuariosPage() {
  const [query, setQuery] = useState<UsuariosQuery>(defaultQuery);
  const [selectedUsuario, setSelectedUsuario] = useState<UsuarioPublic | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const { confirm, notify } = useToast();

  const stableQuery = useMemo(() => query, [query]);
  
  const {
    usuarios,
    total,
    error,
    isLoading,
    isMutating,
    updateUsuario,
    assignRol,
    deleteUsuario,
  } = useUsuarios(stableQuery);

  const totalPages = Math.max(1, Math.ceil(total / query.limit));

  const updateQuery = (patch: Partial<UsuariosQuery>) => {
    setQuery((current) => ({ ...current, ...patch }));
  };

  const handleSubmit = async (values: UsuarioUpdate, newRole: string | null) => {
    if (!selectedUsuario) return;

    try {
      // First update info
      await updateUsuario(selectedUsuario.id, values);
      
      // If role changed, update it too
      if (newRole) {
         await assignRol(selectedUsuario.id, newRole);
      }
      
      setSelectedUsuario(null);
      setIsFormOpen(false);
      notify('success', 'Usuario actualizado correctamente.');
    } catch (requestError) {
      notify(
        'error',
          requestError instanceof Error
            ? requestError.message
            : 'No se pudo actualizar el usuario.',
      );
    }
  };

  const handleDelete = async (u: UsuarioPublic) => {
    const confirmed = await confirm({
      confirmLabel: 'Dar de baja',
      message: `¿Estás seguro que deseas dar de baja al usuario "${u.nombre}"?`,
      title: 'Dar de baja usuario',
      type: 'danger',
    });
    if (confirmed) {
        try {
        await deleteUsuario(u.id);
        notify('success', `El usuario "${u.nombre}" fue dado de baja correctamente.`);
        } catch (requestError) {
        notify(
            'error',
            requestError instanceof Error
                ? requestError.message
                : 'No se pudo dar de baja al usuario.',
        );
        }
    }
  };

  const handleEdit = (u: UsuarioPublic) => {
    setSelectedUsuario(u);
    setIsFormOpen(true);
  };

  return (
    <section className="space-y-6 animate-in fade-in duration-300 pb-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div>
          <span className="section-kicker">Administración</span>
          <h2 className="text-3xl font-black text-charcoal mb-2">Personal y Usuarios</h2>
          <p className="text-muted">Gestión de accesos, perfiles de clientes y empleados.</p>
        </div>
        <div className="flex gap-4">
          <div className="bg-primary/10 text-primary-dark px-4 py-3 rounded-lg flex flex-col items-center justify-center min-w-[100px]">
            <span className="text-xs font-bold uppercase tracking-wide">Total</span>
            <strong className="text-2xl font-black">{total}</strong>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <section className="p-6">
          <div className="flex flex-wrap gap-4 mb-6 bg-gray-50 p-4 rounded-lg items-end">
            <label className="flex flex-col flex-1 min-w-[200px]">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Filtrar por Rol</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary outline-none bg-white font-medium text-charcoal"
                value={query.rol || ''}
                onChange={(e) => {
                    const val = e.target.value;
                    updateQuery({ rol: val === '' ? undefined : val, page: 1 });
                }}
              >
                <option value="">Todos los roles</option>
                <option value="ADMIN">Administradores</option>
                <option value="STOCK">Stock y Cocina</option>
                <option value="PEDIDOS">Caja y Mostrador</option>
                <option value="CLIENT">Clientes Registrados</option>
              </select>
            </label>
            <label className="flex flex-col w-32">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Por página</span>
              <select
                className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary outline-none bg-white font-medium text-charcoal"
                value={query.limit}
                onChange={(event) => updateQuery({ limit: Number(event.target.value), page: 1 })}
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </label>
          </div>

          {error ? <div className="bg-red-50 text-red-700 p-4 rounded-md mb-6">{error}</div> : null}

          <div>
             <UsuariosTable
                usuarios={usuarios}
                isLoading={isLoading}
                onEdit={handleEdit}
                onDelete={handleDelete}
             />
          </div>

          <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-100">
            <button
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm text-charcoal"
              type="button"
              disabled={query.page <= 1 || isLoading}
              onClick={() => updateQuery({ page: query.page - 1 })}
            >
              Anterior
            </button>
            <span className="text-sm font-medium text-gray-500">
              Página {query.page} de {totalPages} ({total} resultados)
            </span>
            <button
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm text-charcoal"
              type="button"
              disabled={query.page >= totalPages || isLoading}
              onClick={() => updateQuery({ page: query.page + 1 })}
            >
              Siguiente
            </button>
          </div>
        </section>
      </div>

      {isFormOpen && selectedUsuario ? (
        <Modal
          kicker="Administración"
          title={`Editar Usuario #${selectedUsuario.id}`}
          size="md"
          onClose={() => {
            setIsFormOpen(false);
            setSelectedUsuario(null);
          }}
        >
          <UsuarioFormModal
            usuario={selectedUsuario}
            isSubmitting={isMutating}
            onSubmit={handleSubmit}
            onCancel={() => {
              setIsFormOpen(false);
              setSelectedUsuario(null);
            }}
          />
        </Modal>
      ) : null}
    </section>
  );
}
