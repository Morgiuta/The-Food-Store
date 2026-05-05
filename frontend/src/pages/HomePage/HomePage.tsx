import './HomePage.css';

export function HomePage() {
  return (
    <section className="home-page">
      <div className="home-page__hero">
        <div>
          <span className="section-kicker">Operacion diaria</span>
          <h2>Control simple para una food store de hamburguesas</h2>
          <p>
            Administra los insumos principales del local y deja preparada la base para sumar
            ventas, proveedores, recetas y reportes.
          </p>
        </div>
      </div>

      <div className="home-page__grid">
        <article className="metric-card">
          <span>Modulo activo</span>
          <strong>Insumos</strong>
          <p>CRUD en memoria con estructura lista para conectar a backend.</p>
        </article>
        <article className="metric-card">
          <span>Arquitectura</span>
          <strong>Modular</strong>
          <p>Componentes, hooks, services, layouts y tipos separados.</p>
        </article>
        <article className="metric-card">
          <span>Identidad visual</span>
          <strong>Burger style</strong>
          <p>Paleta naranja, cheddar, crema y detalles oscuros.</p>
        </article>
      </div>
    </section>
  );
}
