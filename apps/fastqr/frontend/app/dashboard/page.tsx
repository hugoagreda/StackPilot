'use client'

import { useEffect, useState } from 'react'
import { fastqrApi, type Overview } from '@/lib/api'

export default function DashboardPage() {
  const [restaurantId, setRestaurantId] = useState('')
  const [token, setToken] = useState('')
  const [overview, setOverview] = useState<Overview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const rid = localStorage.getItem('fastqr_restaurant_id') ?? ''
    const auth = localStorage.getItem('fastqr_token') ?? ''

    setRestaurantId(rid)
    setToken(auth)

    if (!rid) {
      setLoading(false)
      return
    }

    fastqrApi
      .getOverview(rid)
      .then(setOverview)
      .catch((err) =>
        setError(err instanceof Error ? err.message : 'Error cargando overview')
      )
      .finally(() => setLoading(false))
  }, [])

  const saveLocalConfig = () => {
    localStorage.setItem('fastqr_restaurant_id', restaurantId.trim())
    localStorage.setItem('fastqr_token', token.trim())
    window.location.reload()
  }

  const cards = [
    { label: 'Total votes', value: overview?.total_votes ?? '-' },
    { label: 'Unique sessions', value: overview?.unique_sessions ?? '-' },
    {
      label: 'Average rating',
      value: overview?.avg_rating ? overview.avg_rating.toFixed(1) : '-',
    },
    { label: 'Total feedback', value: overview?.total_feedback ?? '-' },
  ]

  return (
    <main className="stack-lg">

      <header className="card">
        <h1 style={{ margin: 0, fontSize: 26 }}>Dashboard</h1>

        <p className="muted" style={{ marginTop: 6 }}>
          Resumen de interacción de tu restaurante.
        </p>
      </header>

      <section className="grid-2">
        {cards.map((card) => (
          <article
            key={card.label}
            className="card"
            style={{
              padding: 20,
              display: 'flex',
              flexDirection: 'column',
              gap: 4,
            }}
          >
            <p className="muted" style={{ margin: 0, fontSize: 13 }}>
              {card.label}
            </p>

            <p
              style={{
                margin: 0,
                fontSize: 32,
                fontWeight: 700,
              }}
            >
              {card.value}
            </p>
          </article>
        ))}
      </section>

      <section className="card">
        <h2 style={{ marginTop: 0 }}>API configuration</h2>

        <p className="muted">
          Configura las credenciales del restaurante para acceder al dashboard.
        </p>

        <div className="grid-2">
          <div>
            <label htmlFor="restaurantId">Restaurant ID</label>
            <input
              id="restaurantId"
              className="input"
              value={restaurantId}
              onChange={(e) => setRestaurantId(e.target.value)}
              placeholder="uuid del restaurante"
            />
          </div>

          <div>
            <label htmlFor="token">JWT token</label>
            <input
              id="token"
              className="input"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="token para Authorization"
            />
          </div>
        </div>

        <div style={{ marginTop: 14 }}>
          <button className="btn btn-primary" onClick={saveLocalConfig}>
            Guardar configuración
          </button>
        </div>
      </section>

      {loading && <p className="muted">Cargando métricas...</p>}

      {error && (
        <p style={{ color: 'var(--danger)', margin: 0 }}>{error}</p>
      )}

    </main>
  )
}