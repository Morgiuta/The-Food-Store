import { FormEvent, useEffect, useState } from 'react';
import type { UsuarioPublic, UsuarioUpdate } from '../../../../types/usuario';

interface UsuarioFormModalProps {
  usuario: UsuarioPublic;
  isSubmitting?: boolean;
  onSubmit: (values: UsuarioUpdate, newRole: string | null) => Promise<void>;
  onCancel: () => void;
}

export function UsuarioFormModal({
  usuario,
  isSubmitting = false,
  onSubmit,
  onCancel,
}: UsuarioFormModalProps) {
  const [nombre, setNombre] = useState('');
  const [email, setEmail] = useState('');
  const [rolNombre, setRolNombre] = useState('');
  
  const [submitAttempted, setSubmitAttempted] = useState(false);

  useEffect(() => {
    setNombre(usuario.nombre);
    setEmail(usuario.email);
    // Asumimos que un usuario tiene 1 rol principal por cómo funciona el UI, o tomamos el primero
    setRolNombre(usuario.roles.length > 0 ? usuario.roles[0].codigo : '');
    setSubmitAttempted(false);
  }, [usuario]);

  const errors = {
    nombre: !nombre.trim() ? 'El nombre es obligatorio.' : '',
    email: !email.trim() ? 'El email es obligatorio.' : !email.includes('@') ? 'Debe ser un correo válido.' : '',
    rol: !rolNombre ? 'Debe seleccionar un rol.' : '',
  };

  const isSubmitDisabled = Boolean(errors.nombre || errors.email || errors.rol) || isSubmitting;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitAttempted(true);

    if (isSubmitDisabled) return;

    const values: UsuarioUpdate = {
      nombre: nombre.trim(),
      email: email.trim(),
    };
    
    // Check if role changed
    const roleChanged = usuario.roles.length === 0 || usuario.roles[0].codigo !== rolNombre;
    
    await onSubmit(values, roleChanged ? rolNombre : null);
  };

  return (
    <form className="flex flex-col h-full bg-white" onSubmit={handleSubmit}>
      <div className="flex-1 overflow-y-auto space-y-6 p-1">
        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">Nombre completo</label>
          <input
            className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.nombre ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
            name="nombre"
            placeholder="Ej: Juan Pérez"
            value={nombre}
            maxLength={80}
            onChange={(e) => setNombre(e.target.value)}
          />
          {submitAttempted && errors.nombre && <p className="text-red-500 text-xs mt-1 font-medium">{errors.nombre}</p>}
        </div>

        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">Correo electrónico</label>
          <input
            type="email"
            className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.email ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
            name="email"
            placeholder="ejemplo@correo.com"
            value={email}
            maxLength={254}
            onChange={(e) => setEmail(e.target.value)}
          />
          {submitAttempted && errors.email && <p className="text-red-500 text-xs mt-1 font-medium">{errors.email}</p>}
        </div>

        <div className="pt-4 border-t border-gray-100 mt-6">
          <label className="block text-sm font-bold text-charcoal mb-2">Asignar Rol</label>
          <select
            className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.rol ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
            value={rolNombre}
            onChange={(e) => setRolNombre(e.target.value)}
          >
            <option value="" disabled>Seleccionar un rol...</option>
            <option value="ADMIN">Administrador (Acceso Total)</option>
            <option value="STOCK">Stock (Gestión de Insumos y Menú)</option>
            <option value="PEDIDOS">Pedidos (Cocina / Mostrador)</option>
            <option value="CLIENT">Cliente Registrado</option>
          </select>
          <p className="text-xs text-gray-500 mt-2">Los cambios de rol cerrarán automáticamente la sesión del usuario para aplicar los nuevos permisos.</p>
          {submitAttempted && errors.rol && <p className="text-red-500 text-xs mt-1 font-medium">{errors.rol}</p>}
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 pt-6 border-t border-gray-100 mt-6">
        <button 
          type="button" 
          onClick={onCancel}
          className="px-6 py-2.5 font-bold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          Cancelar
        </button>
        <button 
          type="submit" 
          disabled={isSubmitDisabled}
          className="px-6 py-2.5 font-bold text-white bg-primary hover:bg-primary-dark rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Guardando...' : 'Guardar cambios'}
        </button>
      </div>
    </form>
  );
}
