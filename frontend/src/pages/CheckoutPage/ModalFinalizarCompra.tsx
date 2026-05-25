import { useState } from 'react';
import { useFormasPago } from '../../hooks/useFormasPago';
import { Modal } from '../../components/ui/Modal/Modal';
import { Button } from '../../components/ui/Button/Button';
import { Wallet, CreditCard, Banknote, HelpCircle } from 'lucide-react';
import type { CartItem } from '../../store/cartStore';

interface ModalFinalizarCompraProps {
  isOpen: boolean;
  onClose: () => void;
  items: CartItem[];
  subtotal: number;
  envio: number;
  isMutating: boolean;
  onConfirm: (formaPagoCodigo: string) => void;
  error?: string | null;
}

const iconMap: Record<string, React.ReactNode> = {
  EFECTIVO: <Banknote size={24} className="text-emerald-600" />,
  TRANSFERENCIA: <Wallet size={24} className="text-blue-600" />,
  MERCADO_PAGO: <CreditCard size={24} className="text-sky-500" />
};

export function ModalFinalizarCompra({
  isOpen,
  onClose,
  items,
  subtotal,
  envio,
  isMutating,
  onConfirm,
  error
}: ModalFinalizarCompraProps) {
  const { formasPago, isLoading: isLoadingFormas } = useFormasPago();
  const [selectedFormaPago, setSelectedFormaPago] = useState<string | null>(null);

  if (!isOpen) return null;

  const total = subtotal + envio;
  const isMercadoPago = selectedFormaPago === 'MERCADO_PAGO';

  const handleConfirm = () => {
    if (selectedFormaPago && !isMercadoPago) {
      onConfirm(selectedFormaPago);
    }
  };

  return (
    <Modal kicker="Pago" title="Resumen del pedido" size="lg" onClose={onClose}>
      <div className="flex flex-col md:flex-row gap-6">
        
        {/* Lado Izquierdo: Resumen de la compra */}
        <div className="flex-1 space-y-4">
           <h3 className="text-sm font-black uppercase text-gray-500">Detalle de items</h3>
           <div className="bg-gray-50 p-4 rounded-lg border border-gray-100 max-h-60 overflow-y-auto space-y-3">
              {items.map((item) => (
                <div key={item.producto.id} className="flex justify-between items-center text-sm font-bold">
                  <div className="flex gap-2 items-center">
                    <span className="w-6 h-6 bg-charcoal text-white rounded-full flex items-center justify-center text-xs">
                       {item.cantidad}
                    </span>
                    <span className="text-charcoal">{item.producto.nombre}</span>
                  </div>
                  <span className="text-charcoal">${item.producto.precio_base * item.cantidad}</span>
                </div>
              ))}
           </div>
           
           <div className="pt-4 border-t border-gray-200 space-y-2 text-sm text-gray-600 font-semibold">
             <div className="flex justify-between">
                <span>Subtotal</span>
                <span>${subtotal}</span>
             </div>
             <div className="flex justify-between">
                <span>Envío</span>
                <span>${envio}</span>
             </div>
             <div className="flex justify-between text-xl font-black text-charcoal pt-2 border-t border-gray-200 mt-2">
                <span>TOTAL A PAGAR</span>
                <span>${total}</span>
             </div>
           </div>
        </div>

        {/* Lado Derecho: Formas de Pago */}
        <div className="w-full md:w-1/2 flex flex-col">
           <h3 className="text-sm font-black uppercase text-gray-500 mb-4">Forma de pago</h3>
           
           <div className="space-y-3 flex-1 overflow-y-auto pr-2">
              {isLoadingFormas ? (
                 <div className="p-4 text-center font-bold text-gray-400 border-2 border-dashed border-gray-200 rounded-lg">Cargando métodos de pago...</div>
              ) : (
                 <>
                    {formasPago.filter(fp => fp.habilitado && fp.codigo === 'EFECTIVO').map(fp => (
                       <label 
                         key={fp.codigo}
                         className={`flex items-center gap-4 p-4 border-2 rounded-xl cursor-pointer transition-all ${
                            selectedFormaPago === fp.codigo ? 'border-primary bg-primary/5' : 'border-gray-200 bg-white hover:border-gray-300'
                         }`}
                       >
                          <input 
                            type="radio" 
                            name="forma_pago" 
                            className="sr-only" 
                            checked={selectedFormaPago === fp.codigo}
                            onChange={() => setSelectedFormaPago(fp.codigo)}
                          />
                          <div className="w-10 h-10 rounded-full bg-white shadow-sm border border-gray-100 flex items-center justify-center shrink-0">
                             {iconMap[fp.codigo] || <HelpCircle size={24} className="text-gray-400" />}
                          </div>
                          <div className="flex-1">
                             <h4 className="font-black text-charcoal">{fp.descripcion}</h4>
                          </div>
                       </label>
                    ))}

                    {/* Hardcoded Mercado Pago Placeholder */}
                    <label 
                       className={`relative overflow-hidden flex items-center gap-4 p-4 border-2 rounded-xl cursor-pointer transition-all ${
                          selectedFormaPago === 'MERCADO_PAGO' ? 'border-[#009EE3] bg-[#009EE3]/5' : 'border-gray-200 bg-white hover:border-gray-300'
                       }`}
                    >
                       <input 
                         type="radio" 
                         name="forma_pago" 
                         className="sr-only" 
                         checked={selectedFormaPago === 'MERCADO_PAGO'}
                         onChange={() => setSelectedFormaPago('MERCADO_PAGO')}
                       />
                       <div className="w-10 h-10 rounded-full bg-[#009EE3]/10 flex items-center justify-center shrink-0">
                          {iconMap['MERCADO_PAGO']}
                       </div>
                       <div className="flex-1">
                          <div className="flex items-center justify-between">
                             <h4 className="font-black text-[#009EE3]">Mercado Pago</h4>
                             <span className="text-[10px] uppercase tracking-wider font-black text-white bg-[#009EE3] px-2 py-0.5 rounded-full">Próximamente</span>
                          </div>
                       </div>
                    </label>
                 </>
              )}
           </div>

           {error && (
             <div className="mt-4 p-3 bg-red-100 border border-red-200 text-red-700 text-sm font-bold rounded-lg text-center">
                {error}
             </div>
           )}

           <div className="mt-6 pt-4 border-t border-gray-100">
              {isMercadoPago ? (
                 <Button className="w-full py-4 text-base bg-[#009EE3] hover:bg-[#008ACA] text-white opacity-50 cursor-not-allowed" disabled>
                    Integración con Mercado Pago en desarrollo
                    {/* TODO: integrar SDK de Mercado Pago aquí con la estructura base del objeto de preferencia de pago. */}
                 </Button>
              ) : (
                 <Button 
                    className="w-full py-4 text-base shadow-lg shadow-primary/25" 
                    disabled={isMutating || !selectedFormaPago}
                    onClick={handleConfirm}
                 >
                    {isMutating ? 'Procesando...' : selectedFormaPago ? 'Confirmar Pedido' : 'Selecciona un método de pago'}
                 </Button>
              )}
              <Button variant="ghost" className="w-full mt-2 text-gray-500 hover:text-gray-800" onClick={onClose} disabled={isMutating}>
                 Cancelar y volver
              </Button>
           </div>
        </div>
      </div>
    </Modal>
  );
}
