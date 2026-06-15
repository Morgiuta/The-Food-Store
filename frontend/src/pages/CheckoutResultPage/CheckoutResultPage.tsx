import { useMemo, useEffect } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { CheckCircle, XCircle, Clock, Loader2 } from 'lucide-react';
import { pedidosService } from '../../services/pedidosService';
import { pagosService } from '../../services/pagosService';

type ResultStatus = 'exito' | 'fallo' | 'pendiente';

interface ResultConfig {
  icon: React.ReactNode;
  title: string;
  message: string;
  accent: string;
}

const CONFIG: Record<ResultStatus, ResultConfig> = {
  exito: {
    icon: <CheckCircle size={64} className="text-emerald-500" />,
    title: '¡Pago aprobado!',
    message:
      'Tu pago se procesó correctamente. Estamos confirmando el pedido con MercadoPago.',
    accent: 'text-emerald-600',
  },
  pendiente: {
    icon: <Clock size={64} className="text-amber-500" />,
    title: 'Pago pendiente',
    message:
      'Tu pago quedó pendiente de acreditación. Te avisaremos cuando se confirme el pedido.',
    accent: 'text-amber-600',
  },
  fallo: {
    icon: <XCircle size={64} className="text-red-500" />,
    title: 'No se pudo procesar el pago',
    message:
      'El pago fue rechazado o cancelado. Podés volver a intentarlo desde tus pedidos.',
    accent: 'text-red-600',
  },
};

const ESTADO_LABEL: Record<string, string> = {
  PENDIENTE: 'Pendiente de pago',
  CONFIRMADO: 'Confirmado',
  EN_PREP: 'En preparación',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
};

export function CheckoutResultPage() {
  const { status } = useParams<{ status: string }>();
  const [searchParams] = useSearchParams();

  const resultStatus: ResultStatus = useMemo(() => {
    if (status === 'exito' || status === 'fallo' || status === 'pendiente') {
      return status;
    }
    return 'pendiente';
  }, [status]);

  const config = CONFIG[resultStatus];
  const externalReference = searchParams.get('external_reference');
  const paymentId = searchParams.get('payment_id');
  const pedidoId = externalReference ? Number(externalReference) : null;

  const {
    data: pedido,
    isLoading: isLoadingPedido,
    isError,
  } = useQuery({
    queryKey: ['pedido', pedidoId],
    queryFn: () => pedidosService.getById(pedidoId as number),
    enabled: pedidoId !== null && Number.isFinite(pedidoId),
    refetchInterval: (query) => {
      const estado = query.state.data?.estado_codigo;
      return estado && estado !== 'PENDIENTE' ? false : 3000;
    },
  });

  const pago = pedido?.pagos?.[pedido.pagos.length - 1];
  const esperandoConfirmacion =
    resultStatus === 'exito' && pedido?.estado_codigo === 'PENDIENTE';

  useEffect(() => {
    if (paymentId && esperandoConfirmacion) {
      pagosService.sincronizar(paymentId).catch(console.error);
    }
  }, [paymentId, esperandoConfirmacion]);

  return (
    <section className="mx-auto flex max-w-xl flex-col items-center px-4 py-16 text-center">
      <div className="mb-6">{config.icon}</div>
      <h1 className={`text-3xl font-black ${config.accent}`}>{config.title}</h1>
      <p className="mt-3 max-w-md font-semibold text-muted">{config.message}</p>

      {pedidoId !== null && (
        <div className="mt-6 w-full rounded-lg border border-border bg-surface p-4 text-sm font-bold text-muted">
          <div className="flex items-center justify-between">
            <span>Pedido</span>
            <span className="text-charcoal">#{pedidoId}</span>
          </div>

          {isLoadingPedido ? (
            <div className="mt-2 flex items-center justify-end gap-2 text-muted">
              <Loader2 size={16} className="animate-spin" />
              <span>Consultando estado…</span>
            </div>
          ) : isError ? (
            <p className="mt-2 text-right text-muted">
              No pudimos consultar el estado ahora. Revisalo en Mis pedidos.
            </p>
          ) : pedido ? (
            <>
              <div className="mt-1 flex items-center justify-between">
                <span>Estado del pedido</span>
                <span className="text-charcoal">
                  {ESTADO_LABEL[pedido.estado_codigo] ?? pedido.estado_codigo}
                </span>
              </div>
              {pago && (
                <div className="mt-1 flex items-center justify-between">
                  <span>Estado del pago</span>
                  <span className="text-charcoal">{pago.mp_status}</span>
                </div>
              )}
            </>
          ) : null}

          {paymentId && (
            <div className="mt-1 flex items-center justify-between">
              <span>ID de pago</span>
              <span className="text-charcoal">{paymentId}</span>
            </div>
          )}

          {esperandoConfirmacion && (
            <div className="mt-3 flex items-center justify-center gap-2 rounded-md bg-surface-warm p-2 text-amber-700">
              <Loader2 size={16} className="animate-spin" />
              <span>Esperando la confirmación de MercadoPago…</span>
            </div>
          )}
        </div>
      )}

      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <Link
          to="/mis-pedidos"
          className="rounded-md bg-primary px-6 py-3 font-black text-white hover:bg-primary-dark"
        >
          Ver mis pedidos
        </Link>
        <Link
          to="/"
          className="rounded-md border border-border bg-white px-6 py-3 font-black text-charcoal hover:bg-surface-warm"
        >
          Volver al catálogo
        </Link>
      </div>
    </section>
  );
}
