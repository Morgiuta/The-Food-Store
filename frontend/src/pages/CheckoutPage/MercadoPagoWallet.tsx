import { useEffect } from 'react';
import { initMercadoPago, Wallet } from '@mercadopago/sdk-react';

let mpInitialized = false;

interface MercadoPagoWalletProps {
  preferenceId: string;
  publicKey: string;
}

/**
 * Renderiza el Wallet Brick oficial de MercadoPago (SDK React).
 * Usa el preference_id de Checkout Pro creado por el backend.
 */
export function MercadoPagoWallet({ preferenceId, publicKey }: MercadoPagoWalletProps) {
  useEffect(() => {
    if (!mpInitialized && publicKey) {
      initMercadoPago(publicKey, { locale: 'es-AR' });
      mpInitialized = true;
    }
  }, [publicKey]);

  if (!publicKey) {
    return (
      <p className="text-center text-sm font-bold text-red-600">
        Falta configurar la clave pública de MercadoPago en el servidor.
      </p>
    );
  }

  return <Wallet initialization={{ preferenceId }} />;
}
