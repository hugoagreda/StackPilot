import Link from 'next/link'

export default function HomePage() {
  return (
    <main className="shell section">

      <section
        className="card"
        style={{
          padding: 40,
          textAlign: 'center',
        }}
      >
        <p className="muted" style={{ margin: 0, fontWeight: 600 }}>
          FastQR
        </p>

        <h1
          style={{
            fontSize: 36,
            margin: '10px 0 16px',
          }}
        >
          Interacción inteligente para restaurantes
        </h1>

        <p
          className="muted"
          style={{
            maxWidth: 520,
            margin: '0 auto 28px',
            fontSize: 16,
          }}
        >
          Convierte tu menú en una experiencia interactiva con QR.
          Los clientes pueden ver la carta, votar platos y participar en promociones.
        </p>

        <div
          style={{
            display: 'flex',
            gap: 12,
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

    </main>
  )
}