import { FormEvent, useEffect, useState } from 'react';
import type { UsuarioCreate, UsuarioPublic, UsuarioRolUpdate, UsuarioUpdate } from '../../../../types/usuario';

interface UsuarioFormModalProps {
  usuario?: UsuarioPublic | null;
  isSubmitting?: boolean;
  onSubmit: (
    values: UsuarioCreate | UsuarioUpdate,
    roleUpdate: UsuarioRolUpdate | null,
  ) => Promise<void>;
  onCancel: () => void;
}

export function UsuarioFormModal({
  usuario,
  isSubmitting = false,
  onSubmit,
  onCancel,
}: UsuarioFormModalProps) {
  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [email, setEmail] = useState('');
  const [celular, setCelular] = useState('');
  const [password, setPassword] = useState('');
  const [rolNombre, setRolNombre] = useState('');
  const [rolExpiresAt, setRolExpiresAt] = useState('');
  
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const isEditing = Boolean(usuario);

  useEffect(() => {
    setNombre(usuario?.nombre ?? '');
    setApellido(usuario?.apellido ?? '');
    setEmail(usuario?.email ?? '');
    setCelular(usuario?.celular ?? '');
    setPassword('');
    setRolNombre(usuario?.roles?.[0]?.codigo ?? 'CLIENT');
    setRolExpiresAt(toInputDateTime(usuario?.roles?.[0]?.expires_at));
    setSubmitAttempted(false);
  }, [usuario]);

  const errors = {
    nombre: !nombre.trim() ? 'El nombre es obligatorio.' : '',
    apellido: !apellido.trim() ? 'El apellido es obligatorio.' : '',
    email: !email.trim() ? 'El email es obligatorio.' : !email.includes('@') ? 'Debe ser un correo válido.' : '',
    password: !isEditing && password.length < 8 ? 'La contraseña debe tener al menos 8 caracteres.' : password && password.length < 8 ? 'La contraseña debe tener al menos 8 caracteres.' : '',
    rol: !rolNombre ? 'Debe seleccionar un rol.' : '',
  };

  const isSubmitDisabled = Boolean(errors.nombre || errors.apellido || errors.email || errors.password || errors.rol) || isSubmitting;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitAttempted(true);

    if (isSubmitDisabled) return;

    const rolePayload: UsuarioRolUpdate = {
      rol_nombre: rolNombre,
      expires_at: rolExpiresAt ? new Date(rolExpiresAt).toISOString() : null,
    };

    if (!isEditing) {
      const values: UsuarioCreate = {
        nombre: nombre.trim(),
        apellido: apellido.trim(),
        email: email.trim(),
        password,
        celular: celular.trim() || null,
        rol_nombre: rolePayload.rol_nombre,
        rol_expires_at: rolePayload.expires_at,
      };
      await onSubmit(values, null);
      return;
    }

    const values: UsuarioUpdate = {
      nombre: nombre.trim(),
      apellido: apellido.trim(),
      email: email.trim(),
      celular: celular.trim() || null,
    };
    if (password) {
      values.password = password;
    }

    const currentRole = usuario?.roles?.[0];
    const currentExpiresAt = toInputDateTime(currentRole?.expires_at);
    const roleChanged = currentRole?.codigo !== rolNombre || currentExpiresAt !== rolExpiresAt;

    await onSubmit(values, roleChanged ? rolePayload : null);
  };

  return (
    <form className="flex flex-col h-full bg-white" onSubmit={handleSubmit}>
      <div className="flex-1 overflow-y-auto space-y-6 p-1">
        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">Nombre</label>
          <input
            className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.nombre ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
            name="nombre"
            placeholder="Ej: Juan"
            value={nombre}
            maxLength={80}
            onChange={(e) => setNombre(e.target.value)}
          />
          {submitAttempted && errors.nombre && <p className="text-red-500 text-xs mt-1 font-medium">{errors.nombre}</p>}
        </div>

        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">Apellido</label>
          <input
            className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.apellido ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
            name="apellido"
            placeholder="Ej: Pérez"
            value={apellido}
            maxLength={80}
            onChange={(e) => setApellido(e.target.value)}
          />
          {submitAttempted && errors.apellido && <p className="text-red-500 text-xs mt-1 font-medium">{errors.apellido}</p>}
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

        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">Celular</label>
          <input
            className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent border-gray-300"
            name="celular"
            placeholder="Ej: 2615551234"
            value={celular}
            maxLength={20}
            onChange={(e) => setCelular(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">
            {isEditing ? 'Nueva contraseña' : 'Contraseña'}
          </label>
          <input
            type="password"
            className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.password ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
            name="password"
            placeholder={isEditing ? 'Dejar vacío para no cambiar' : 'Mínimo 8 caracteres'}
            value={password}
            maxLength={128}
            onChange={(e) => setPassword(e.target.value)}
          />
          {submitAttempted && errors.password && <p className="text-red-500 text-xs mt-1 font-medium">{errors.password}</p>}
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
          {submitAttempted && errors.rol && <p className="text-red-500 text-xs mt-1 font-medium">{errors.rol}</p>}
        </div>

        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">Vencimiento del rol</label>
          <input
            type="datetime-local"
            className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent border-gray-300"
            value={rolExpiresAt}
            onChange={(e) => setRolExpiresAt(e.target.value)}
          />
          <p className="text-xs text-gray-500 mt-2">Dejar vacío para que el rol no expire.</p>
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
          {isSubmitting ? 'Guardando...' : isEditing ? 'Guardar cambios' : 'Crear usuario'}
        </button>
      </div>
    </form>
  );
}

function toInputDateTime(value?: string | null): string {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const offsetMs = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}
