import { Button } from '../../../../components/ui/Button/Button';
import { EmptyState } from '../../../../components/ui/EmptyState/EmptyState';
import type { UsuarioPublic } from '../../../../types/usuario';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface UsuariosTableProps {
  usuarios: UsuarioPublic[];
  isLoading?: boolean;
  onEdit: (usuario: UsuarioPublic) => void;
  onDelete: (usuario: UsuarioPublic) => void;
}

const roleColors: Record<string, string> = {
  ADMIN: 'bg-purple-100 text-purple-800 border-purple-200',
  STOCK: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  PEDIDOS: 'bg-orange-100 text-orange-800 border-orange-200',
  CLIENT: 'bg-blue-100 text-blue-800 border-blue-200',
};

export function UsuariosTable({
  usuarios,
  isLoading = false,
  onEdit,
  onDelete,
}: UsuariosTableProps) {
  
  if (isLoading) {
    return <div className="p-8 text-center text-gray-500 bg-gray-50 rounded-lg">Cargando usuarios...</div>;
  }

  if (usuarios.length === 0) {
    return (
      <EmptyState
        title="No hay usuarios encontrados"
        description="No existen usuarios que coincidan con los filtros aplicados."
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse table-fixed">
        <thead>
          <tr className="bg-gray-50 border-y border-gray-200">
            <th className="p-4 font-bold text-sm text-charcoal w-[10%] text-center">ID</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[25%]">Usuario</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[25%]">Contacto</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[15%]">Roles</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[10%]">Registro</th>
            <th className="p-4 font-bold text-sm text-charcoal w-[15%] text-right" aria-label="Acciones">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {usuarios.map((u) => (
            <tr key={u.id} className={`hover:bg-gray-50/50 transition-colors ${!u.is_active ? 'opacity-60 bg-gray-50' : ''}`}>
              <td className="p-4 text-center text-sm font-bold text-gray-400">
                #{u.id}
              </td>
              <td className="p-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold shrink-0 ${!u.is_active ? 'bg-gray-400' : 'bg-charcoal'}`}>
                     {u.nombre.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <strong className={`block mb-0.5 ${!u.is_active ? 'line-through text-gray-500' : 'text-charcoal'}`}>{u.nombre} {u.apellido}</strong>
                    {!u.is_active && <span className="text-xs font-bold text-red-500 uppercase">Dado de baja</span>}
                  </div>
                </div>
              </td>
              <td className="p-4">
                <div className="space-y-1">
                  <a href={`mailto:${u.email}`} className="block text-sm font-medium text-primary hover:underline">{u.email}</a>
                  {u.celular ? <span className="block text-xs font-semibold text-gray-500">{u.celular}</span> : null}
                </div>
              </td>
              <td className="p-4">
                <div className="flex flex-wrap gap-1.5">
                  {u.roles.length === 0 ? (
                    <span className="text-xs italic text-gray-400">Sin roles</span>
                  ) : (
                    u.roles.map(r => {
                      const colorClass = roleColors[r.codigo] || 'bg-gray-100 text-gray-800 border-gray-200';
                      return (
                        <span key={r.codigo} className="space-y-1">
                          <span className={`inline-flex px-2.5 py-1 text-xs font-bold rounded-full border ${colorClass}`}>
                            {r.codigo}
                          </span>
                          {r.expires_at ? (
                            <span className="block text-[11px] font-semibold text-gray-500">
                              vence {format(new Date(r.expires_at), 'dd/MM/yyyy', { locale: es })}
                            </span>
                          ) : null}
                        </span>
                      );
                    })
                  )}
                </div>
              </td>
              <td className="p-4 text-sm text-gray-500">
                 {format(new Date(u.created_at), 'dd/MM/yyyy', { locale: es })}
              </td>
              <td className="p-4">
                <div className="flex items-center justify-end gap-2">
                  <Button
                    variant="secondary"
                    onClick={() => onEdit(u)}
                    disabled={!u.is_active}
                  >
                    Editar
                  </Button>
                  <Button 
                    variant="danger" 
                    onClick={() => onDelete(u)}
                    disabled={!u.is_active}
                  >
                    Baja
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
