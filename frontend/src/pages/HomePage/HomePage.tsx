import { Clock, Package, CircleDollarSign, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend
} from 'recharts';
import { useAuthStore } from '../../store/authStore';
import { useDashboard } from '../../hooks/useDashboard';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const estadoStyles: Record<string, string> = {
  PENDIENTE: 'bg-yellow-100 text-yellow-800',
  CONFIRMADO: 'bg-blue-100 text-blue-800',
  EN_PREP: 'bg-orange-100 text-orange-800',
  ENTREGADO: 'bg-emerald-100 text-emerald-800',
  CANCELADO: 'bg-gray-100 text-gray-800',
};

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
  }).format(value);
}

export function HomePage() {
  const { user } = useAuthStore();
  const { metrics, pedidosRecientes, isLoadingMetrics, isLoadingRecientes } = useDashboard();

  return (
    <section className="space-y-8 animate-in fade-in duration-500 pb-12">
      {/* Encabezado */}
      <div>
        <h1 className="text-3xl font-black text-charcoal">
          Bienvenido, {user?.nombre || 'Administrador'}
        </h1>
        <p className="text-muted mt-1">Aquí tienes un resumen de la operación de hoy.</p>
      </div>

      {/* Métricas */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Metric 1: Pedidos Activos */}
        <article className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-start gap-4">
          <div className="p-3 rounded-xl bg-orange-100 text-orange-600 shrink-0">
            <Clock size={24} />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">Pedidos Activos</p>
            {isLoadingMetrics ? (
              <div className="h-8 w-16 bg-gray-200 animate-pulse rounded-md"></div>
            ) : (
              <p className="text-3xl font-black text-charcoal">{metrics?.pedidosActivos}</p>
            )}
          </div>
        </article>

        {/* Metric 3: Ingresos del Día */}
        <article className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-start gap-4">
          <div className="p-3 rounded-xl bg-emerald-100 text-emerald-600 shrink-0">
            <CircleDollarSign size={24} />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">Ingresos (Hoy)</p>
            {isLoadingMetrics ? (
              <div className="h-8 w-24 bg-gray-200 animate-pulse rounded-md"></div>
            ) : (
              <p className="text-3xl font-black text-charcoal">{formatCurrency(metrics?.ingresosDia || 0)}</p>
            )}
          </div>
        </article>

        {/* Metric 5: Productos bajo stock */}
        <article className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-start gap-4">
          <div className="p-3 rounded-xl bg-red-100 text-red-600 shrink-0">
            <Package size={24} />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">Stock Bajo</p>
            {isLoadingMetrics ? (
              <div className="h-8 w-16 bg-gray-200 animate-pulse rounded-md"></div>
            ) : (
              <p className="text-3xl font-black text-charcoal">{metrics?.productosBajoStock}</p>
            )}
          </div>
        </article>
      </div>

      {/* Gráficos y Estadísticas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <article className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-black text-charcoal mb-4">Ingresos por Día</h2>
          <div className="h-64">
            {isLoadingMetrics ? (
              <div className="w-full h-full bg-gray-100 animate-pulse rounded-xl" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metrics?.ventasPorDia || []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="fecha" />
                  <YAxis tickFormatter={(val) => `$${val}`} />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Line type="monotone" dataKey="ingresos" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </article>

        <article className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-black text-charcoal mb-4">Productos Más Vendidos</h2>
          <div className="h-64">
            {isLoadingMetrics ? (
              <div className="w-full h-full bg-gray-100 animate-pulse rounded-xl" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics?.productosTop || []} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" />
                  <YAxis dataKey="nombre" type="category" width={100} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="cantidad_vendida" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </article>
        
        <article className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-black text-charcoal mb-4">Pedidos por Estado</h2>
          <div className="h-64">
            {isLoadingMetrics ? (
              <div className="w-full h-full bg-gray-100 animate-pulse rounded-xl" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={metrics?.pedidosPorEstado || []}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="cantidad"
                    nameKey="estado"
                  >
                    {(metrics?.pedidosPorEstado || []).map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </article>

        <article className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-black text-charcoal mb-4">Ingresos por Forma de Pago</h2>
          <div className="h-64">
            {isLoadingMetrics ? (
              <div className="w-full h-full bg-gray-100 animate-pulse rounded-xl" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics?.ingresosPorFormaPago || []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="forma_pago" />
                  <YAxis tickFormatter={(val) => `$${val}`} />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Bar dataKey="ingresos" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </article>
      </div>

      {/* Tabla de últimos pedidos */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <h2 className="text-lg font-black text-charcoal">Últimos pedidos</h2>
          <Link to="/admin/pedidos" className="text-sm font-bold text-primary hover:text-primary-dark inline-flex items-center gap-1">
            Ver todos <ChevronRight size={16} />
          </Link>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse table-fixed">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100 text-xs uppercase tracking-wider text-gray-500 font-bold">
                <th className="px-6 py-4 w-[15%]">ID</th>
                <th className="px-6 py-4 w-[40%]">Cliente</th>
                <th className="px-6 py-4 w-[25%]">Estado</th>
                <th className="px-6 py-4 w-[20%] text-right">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {isLoadingRecientes ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-6 py-4"><div className="h-4 w-8 bg-gray-200 rounded"></div></td>
                    <td className="px-6 py-4"><div className="h-4 w-32 bg-gray-200 rounded"></div></td>
                    <td className="px-6 py-4"><div className="h-6 w-20 bg-gray-200 rounded-full"></div></td>
                    <td className="px-6 py-4 flex justify-end"><div className="h-4 w-16 bg-gray-200 rounded"></div></td>
                  </tr>
                ))
              ) : pedidosRecientes.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500 font-medium">
                    No hay pedidos recientes.
                  </td>
                </tr>
              ) : (
                pedidosRecientes.map((pedido) => (
                  <tr 
                    key={pedido.id} 
                    className="hover:bg-gray-50 transition-colors group cursor-pointer"
                    onClick={() => {
                      window.location.href = '/admin/pedidos';
                    }}
                  >
                    <td className="px-6 py-4 font-bold text-charcoal">#{pedido.id}</td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-charcoal">{pedido.usuario_nombre || `Cliente #${pedido.usuario_id}`}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(pedido.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-black ${estadoStyles[pedido.estado_codigo] || 'bg-gray-100 text-gray-800'}`}>
                        {pedido.estado_codigo}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-black text-charcoal text-right group-hover:text-primary transition-colors">
                      {formatCurrency(pedido.total)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
