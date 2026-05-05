import { FormEvent, useEffect, useState } from 'react';
import { Button } from '../../../../components/ui/Button/Button';
import { Input } from '../../../../components/ui/Input/Input';
import { Textarea } from '../../../../components/ui/Textarea/Textarea';
import type { Supply, SupplyFormValues } from '../../../../types/supply';
import './SupplyForm.css';

const initialValues: SupplyFormValues = {
  name: '',
  description: '',
  quantity: 0,
};

interface SupplyFormProps {
  selectedSupply: Supply | null;
  onSubmit: (values: SupplyFormValues) => void;
  onCancelEdit: () => void;
}

export function SupplyForm({ selectedSupply, onSubmit, onCancelEdit }: SupplyFormProps) {
  const [values, setValues] = useState<SupplyFormValues>(initialValues);

  useEffect(() => {
    setValues(
      selectedSupply
        ? {
            name: selectedSupply.name,
            description: selectedSupply.description,
            quantity: selectedSupply.quantity,
          }
        : initialValues,
    );
  }, [selectedSupply]);

  const isEditing = Boolean(selectedSupply);
  const isSubmitDisabled = !values.name.trim() || values.quantity < 0;

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (isSubmitDisabled) {
      return;
    }

    onSubmit({
      name: values.name.trim(),
      description: values.description.trim(),
      quantity: Number(values.quantity),
    });

    setValues(initialValues);
  };

  return (
    <form className="supply-form" onSubmit={handleSubmit}>
      <div className="supply-form__header">
        <div>
          <span className="section-kicker">Stock</span>
          <h2>{isEditing ? 'Editar insumo' : 'Nuevo insumo'}</h2>
        </div>
        {isEditing ? (
          <Button variant="ghost" onClick={onCancelEdit}>
            Cancelar
          </Button>
        ) : null}
      </div>

      <Input
        label="Nombre"
        name="name"
        placeholder="Ej: Pan brioche"
        value={values.name}
        onChange={(event) => setValues((current) => ({ ...current, name: event.target.value }))}
      />

      <Textarea
        label="Descripcion"
        name="description"
        placeholder="Detalle breve del insumo"
        rows={4}
        value={values.description}
        onChange={(event) =>
          setValues((current) => ({ ...current, description: event.target.value }))
        }
      />

      <Input
        label="Cantidad"
        name="quantity"
        min={0}
        type="number"
        value={values.quantity}
        onChange={(event) =>
          setValues((current) => ({ ...current, quantity: Number(event.target.value) }))
        }
      />

      <Button type="submit" disabled={isSubmitDisabled}>
        {isEditing ? 'Guardar cambios' : 'Crear insumo'}
      </Button>
    </form>
  );
}
