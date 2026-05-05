import { useMemo, useState } from 'react';
import { suppliesService } from '../services/suppliesService';
import type { Supply, SupplyFormValues } from '../types/supply';

export function useSupplies() {
  const [supplies, setSupplies] = useState<Supply[]>(() => suppliesService.getAll());

  const totalUnits = useMemo(
    () => supplies.reduce((total, supply) => total + supply.quantity, 0),
    [supplies],
  );

  const createSupply = (values: SupplyFormValues) => {
    const createdSupply = suppliesService.create(values);
    setSupplies((current) => [createdSupply, ...current]);
  };

  const updateSupply = (id: string, values: SupplyFormValues) => {
    const updatedSupply = suppliesService.update(id, values);
    setSupplies((current) =>
      current.map((supply) => (supply.id === id ? updatedSupply : supply)),
    );
  };

  const deleteSupply = (id: string) => {
    suppliesService.remove(id);
    setSupplies((current) => current.filter((supply) => supply.id !== id));
  };

  return {
    supplies,
    totalUnits,
    createSupply,
    updateSupply,
    deleteSupply,
  };
}
