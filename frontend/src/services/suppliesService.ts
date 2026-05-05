import { mockSupplies } from '../data/mockSupplies';
import type { Supply } from '../types/supply';

let supplies = [...mockSupplies];

export const suppliesService = {
  getAll(): Supply[] {
    return [...supplies];
  },

  create(input: Omit<Supply, 'id'>): Supply {
    const supply: Supply = {
      ...input,
      id: crypto.randomUUID(),
    };

    supplies = [supply, ...supplies];
    return supply;
  },

  update(id: string, input: Omit<Supply, 'id'>): Supply {
    const updated: Supply = { id, ...input };
    supplies = supplies.map((supply) => (supply.id === id ? updated : supply));
    return updated;
  },

  remove(id: string): void {
    supplies = supplies.filter((supply) => supply.id !== id);
  },
};
