import Link from 'next/link'

export default function HomePage() {
  return (
    <main className="shell section">
      <div className="stack-lg">
        <section
          className="card"
          style={{
            padding: '60px 40px',
            textAlign: 'center',
          }}
        >
          <div style={{ marginBottom: 24 }}>
            <p className="text-sm font-medium" style={{ color: 'var(--primary)', margin: 0, marginBottom: 12 }}>
              FastQR
            </p>
            <h1>Interacción inteligente para restaurantes</h1>
          </div>

          <p
            className="muted"
            style={{
              maxWidth: 560,
              margin: '0 auto 32px',
              fontSize: 16,
              lineHeight: 1.6,
            }}
          >
            Convierte tu menú en una experiencia interactiva con QR.
            Los clientes pueden ver la carta, votar platos y participar en promociones.
          </p>

          <div
            style={{
              display: 'flex',
              gap: 16,
              justifyContent: 'center',
              flexWrap: 'wrap',
            }}
          >
            <Link href="/dashboard" className="btn btn-primary">
              Ir al dashboard
            </Link>

            <Link href="/t/demo-token" className="btn btn-soft">
              Ver demo cliente
            </Link>
          </div>
        </section>

        <section className="card" style={{ padding: '40px' }}>
          <h2 style={{ marginBottom: 24 }}>Características principales</h2>
          <div className="grid-3">
            <div>
              <h3 style={{ color: 'var(--primary)', marginBottom: 8 }}>QR Digital</h3>
              <p className="muted">Menú interactivo accesible desde cualquier dispositivo móvil.</p>
            </div>
            <div>
              <h3 style={{ color: 'var(--primary)', marginBottom: 8 }}>Votaciones</h3>
              <p className="muted">Los clientes pueden votar sus platos favoritos en tiempo real.</p>
            </div>
            <div>
              <h3 style={{ color: 'var(--primary)', marginBottom: 8 }}>Analytics</h3>
              <p className="muted">Métricas detalladas sobre preferencias de clientes.</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
