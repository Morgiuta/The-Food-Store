export function HomePage() {
  return (
    <section className="space-y-8 animate-in fade-in duration-500">
      <div className="bg-primary/10 border border-primary/20 rounded-2xl p-8 lg:p-12">
        <div className="max-w-3xl">
          <span className="section-kicker">Operación diaria</span>
          <h2 className="text-3xl lg:text-4xl font-extrabold text-charcoal mt-2 mb-4 leading-tight">
            Control simple para una food store de hamburguesas
          </h2>
          <p className="text-muted text-lg">
            Administra los insumos principales del local y deja preparada la base para sumar
            ventas, proveedores, recetas y reportes.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <article className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col hover:shadow-md transition-shadow">
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Módulo activo</span>
          <strong className="text-2xl font-black text-primary mb-3">Insumos</strong>
          <p className="text-gray-600 text-sm">CRUD conectado a backend mediante React Query y validado con Tailwind.</p>
        </article>

        <article className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col hover:shadow-md transition-shadow">
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Arquitectura</span>
          <strong className="text-2xl font-black text-primary mb-3">Modular</strong>
          <p className="text-gray-600 text-sm">Componentes, hooks, services, layouts y estado global con Zustand.</p>
        </article>

        <article className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col hover:shadow-md transition-shadow">
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Identidad visual</span>
          <strong className="text-2xl font-black text-primary mb-3">Burger style</strong>
          <p className="text-gray-600 text-sm">Paleta naranja, cheddar, crema y detalles oscuros con Tailwind CSS.</p>
        </article>
      </div>
    </section>
  );
}
