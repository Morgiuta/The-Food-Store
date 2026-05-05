export interface Supply {
  id: string;
  name: string;
  description: string;
  quantity: number;
}

export type SupplyFormValues = Omit<Supply, 'id'>;
