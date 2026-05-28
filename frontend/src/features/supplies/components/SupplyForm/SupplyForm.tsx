import { FormEvent, useEffect, useState } from 'react';
import type { Supply, SupplyFormValues } from '../../../../types/supply';

const initialValues: SupplyFormValues = {
  nombre: '',
  descripcion: '',
  es_alergeno: false,
  stock_actual: 0,
  unidad: 'unidad',
};

interface SupplyFormProps {
  selectedSupply: Supply | null;
  isSubmitting?: boolean;
  existingNames: string[];
  onSubmit: (values: SupplyFormValues) => Promise<void>;
  onCancelEdit: () => void;
}

export function SupplyForm({
  selectedSupply,
  isSubmitting = false,
  existingNames,
  onSubmit,
  onCancelEdit,
}: SupplyFormProps) {
  const [values, setValues] = useState<SupplyFormValues>(initialValues);
  const [submitAttempted, setSubmitAttempted] = useState(false);

  useEffect(() => {
    setValues(
      selectedSupply
        ? {
            nombre: selectedSupply.nombre,
            descripcion: selectedSupply.descripcion ?? '',
            es_alergeno: selectedSupply.es_alergeno,
            stock_actual: selectedSupply.stock_actual ?? 0,
            unidad: selectedSupply.unidad ?? 'unidad',
          }
        : initialValues,
    );
    setSubmitAttempted(false);
  }, [selectedSupply]);

  const isEditing = Boolean(selectedSupply);
  const normalizedName = values.nombre.trim().toLowerCase();
  const hasDuplicatedName = existingNames.some(
    (name) => name.toLowerCase() === normalizedName,
  );
  
  const errors = {
    nombre: !values.nombre.trim()
      ? 'El nombre es obligatorio.'
      : values.nombre.trim().length < 2
        ? 'Debe tener al menos 2 caracteres.'
        : hasDuplicatedName
          ? 'Ya existe un ingrediente activo con ese nombre.'
          : '',
    descripcion:
      values.descripcion.trim().length > 300
        ? 'La descripción no puede superar 300 caracteres.'
        : '',
    stock_actual: values.stock_actual < 0 ? 'El stock no puede ser negativo.' : '',
  };
  
  const isSubmitDisabled = Boolean(errors.nombre || errors.descripcion || errors.stock_actual) || isSubmitting;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitAttempted(true);

    if (isSubmitDisabled) {
      return;
    }

    await onSubmit({
      nombre: values.nombre.trim(),
      descripcion: values.descripcion.trim(),
      es_alergeno: values.es_alergeno,
      stock_actual: Number(values.stock_actual),
      unidad: values.unidad,
    });

    setValues(initialValues);
    setSubmitAttempted(false);
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div>
        <label className="block text-sm font-bold text-charcoal mb-2">Nombre del ingrediente</label>
        <input
          className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.nombre ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
          name="nombre"
          placeholder="Ej: Queso cheddar"
          value={values.nombre}
          maxLength={100}
          onChange={(event) => setValues((current) => ({ ...current, nombre: event.target.value }))}
        />
        {submitAttempted && errors.nombre && <p className="text-red-500 text-xs mt-1 font-medium">{errors.nombre}</p>}
      </div>

      <div>
        <label className="block text-sm font-bold text-charcoal mb-2">Descripción</label>
        <textarea
          className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-y ${submitAttempted && errors.descripcion ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
          name="descripcion"
          placeholder="Detalle breve del ingrediente"
          rows={3}
          value={values.descripcion}
          maxLength={300}
          onChange={(event) =>
            setValues((current) => ({ ...current, descripcion: event.target.value }))
          }
        />
        {submitAttempted && errors.descripcion && <p className="text-red-500 text-xs mt-1 font-medium">{errors.descripcion}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">Stock Actual</label>
          <input
            type="number"
            min="0"
            step="0.01"
            className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.stock_actual ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
            name="stock_actual"
            value={values.stock_actual}
            onChange={(event) => setValues((current) => ({ ...current, stock_actual: Number(event.target.value) }))}
          />
          {submitAttempted && errors.stock_actual && <p className="text-red-500 text-xs mt-1 font-medium">{errors.stock_actual}</p>}
        </div>

        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">Unidad de medida</label>
          <select
            className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent border-gray-300 bg-white"
            name="unidad"
            value={values.unidad}
            onChange={(event) =>
              setValues((current) => ({
                ...current,
                unidad: event.target.value as SupplyFormValues['unidad'],
              }))
            }
          >
            <option value="unidad">Unidad</option>
            <option value="kg">Kilogramos</option>
            <option value="litros">Litros</option>
            <option value="gramos">Gramos</option>
            <option value="ml">Mililitros</option>
          </select>
        </div>

        <div className="flex items-end pb-3">
          <label className="flex items-center gap-3 cursor-pointer group">
            <div className="relative flex items-center justify-center">
              <input
                checked={values.es_alergeno}
                type="checkbox"
                className="peer sr-only"
                onChange={(event) =>
                  setValues((current) => ({ ...current, es_alergeno: event.target.checked }))
                }
              />
              <div className="w-6 h-6 border-2 border-gray-300 rounded peer-checked:bg-orange-500 peer-checked:border-orange-500 transition-colors"></div>
              <svg className="absolute w-4 h-4 text-white opacity-0 peer-checked:opacity-100 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span className="font-medium text-charcoal group-hover:text-orange-600 transition-colors">Marcar como alérgeno</span>
          </label>
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 pt-6 border-t border-gray-100">
        <button 
          type="button" 
          onClick={onCancelEdit}
          className="px-6 py-2.5 font-bold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          Cancelar
        </button>
        <button 
          type="submit" 
          disabled={isSubmitDisabled}
          className="px-6 py-2.5 font-bold text-white bg-primary hover:bg-primary-dark rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Guardando...' : isEditing ? 'Guardar cambios' : 'Crear ingrediente'}
        </button>
      </div>
    </form>
  );
}
