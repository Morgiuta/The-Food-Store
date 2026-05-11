import { FormEvent, useEffect, useState } from 'react';
import { Button } from '../../../../components/ui/Button/Button';
import { Input } from '../../../../components/ui/Input/Input';
import { Textarea } from '../../../../components/ui/Textarea/Textarea';
import type { Supply, SupplyFormValues } from '../../../../types/supply';
import './SupplyForm.css';

const initialValues: SupplyFormValues = {
  nombre: '',
  descripcion: '',
  es_alergeno: false,
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
          ? 'Ya existe un insumo activo con ese nombre.'
          : '',
    descripcion:
      values.descripcion.trim().length > 300
        ? 'La descripcion no puede superar 300 caracteres.'
        : '',
  };
  const isSubmitDisabled = Boolean(errors.nombre || errors.descripcion) || isSubmitting;

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
    });

    setValues(initialValues);
    setSubmitAttempted(false);
  };

  return (
    <form className="supply-form" onSubmit={handleSubmit}>
      <Input
        label="Nombre"
        name="nombre"
        placeholder="Ej: Queso cheddar"
        value={values.nombre}
        error={submitAttempted ? errors.nombre : undefined}
        maxLength={100}
        onChange={(event) => setValues((current) => ({ ...current, nombre: event.target.value }))}
      />

      <Textarea
        label="Descripcion"
        name="descripcion"
        placeholder="Detalle breve del insumo"
        rows={4}
        value={values.descripcion}
        error={submitAttempted ? errors.descripcion : undefined}
        maxLength={300}
        onChange={(event) =>
          setValues((current) => ({ ...current, descripcion: event.target.value }))
        }
      />

      <label className="supply-form__check">
        <input
          checked={values.es_alergeno}
          type="checkbox"
          onChange={(event) =>
            setValues((current) => ({ ...current, es_alergeno: event.target.checked }))
          }
        />
        <span>Marcar como alergeno</span>
      </label>

      <div className="supply-form__actions">
        <Button variant="ghost" onClick={onCancelEdit}>
          Cancelar
        </Button>
        <Button type="submit" disabled={isSubmitDisabled}>
          {isSubmitting ? 'Guardando...' : isEditing ? 'Guardar cambios' : 'Crear insumo'}
        </Button>
      </div>
    </form>
  );
}
