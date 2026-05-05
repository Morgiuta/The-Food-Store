import { useState } from 'react';
import { SupplyForm } from '../../features/supplies/components/SupplyForm/SupplyForm';
import { SuppliesTable } from '../../features/supplies/components/SuppliesTable/SuppliesTable';
import { useSupplies } from '../../hooks/useSupplies';
import type { Supply, SupplyFormValues } from '../../types/supply';
import './SuppliesPage.css';

export function SuppliesPage() {
  const { supplies, totalUnits, createSupply, updateSupply, deleteSupply } = useSupplies();
  const [selectedSupply, setSelectedSupply] = useState<Supply | null>(null);

  const handleSubmit = (values: SupplyFormValues) => {
    if (selectedSupply) {
      updateSupply(selectedSupply.id, values);
      setSelectedSupply(null);
      return;
    }

    createSupply(values);
  };

  return (
    <section className="supplies-page">
      <div className="supplies-page__heading">
        <div>
          <span className="section-kicker">Inventario</span>
          <h2>Insumos</h2>
          <p>Alta, listado, edicion y baja de insumos para la operacion del local.</p>
        </div>
        <div className="supplies-page__summary">
          <span>Total unidades</span>
          <strong>{totalUnits}</strong>
        </div>
      </div>

      <div className="supplies-page__content">
        <SupplyForm
          selectedSupply={selectedSupply}
          onSubmit={handleSubmit}
          onCancelEdit={() => setSelectedSupply(null)}
        />
        <section className="supplies-page__list">
          <div className="supplies-page__list-header">
            <h3>Listado de insumos</h3>
            <span>{supplies.length} items</span>
          </div>
          <SuppliesTable
            supplies={supplies}
            onEdit={setSelectedSupply}
            onDelete={deleteSupply}
          />
        </section>
      </div>
    </section>
  );
}
