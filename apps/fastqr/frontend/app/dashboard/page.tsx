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

      <div>
        <h1>Dashboard</h1>
        <p className="muted">Resumen de interacción de tu restaurante.</p>
      </div>

      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p className="muted">Cargando métricas...</p>
        </div>
      )}

      {!loading && (
        <>
          <section className="grid-2">
            {cards.map((card) => (
              <article
                key={card.label}
                className="card"
                style={{
                  padding: 24,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <p className="text-sm muted" style={{ margin: 0 }}>
                  {card.label}
                </p>

                <p
                  style={{
                    margin: '8px 0 0 0',
                    fontSize: 36,
                    fontWeight: 700,
                    color: 'var(--primary)',
                  }}
                >
                  {card.value}
                </p>
              </article>
            ))}
          </section>

          <section className="card">
            <h2>API Configuration</h2>
            <p className="muted" style={{ marginBottom: 24 }}>
              Configura las credenciales del restaurante para acceder al dashboard.
            </p>

            <div className="grid-2" style={{ marginBottom: 24 }}>
              <div>
                <label htmlFor="restaurantId" style={{ display: 'block', marginBottom: 8, fontSize: 14, fontWeight: 500 }}>
                  Restaurant ID
                </label>
                <input
                  id="restaurantId"
                  className="input"
                  value={restaurantId}
                  onChange={(e) => setRestaurantId(e.target.value)}
                  placeholder="uuid del restaurante"
                />
              </div>

              <div>
                <label htmlFor="token" style={{ display: 'block', marginBottom: 8, fontSize: 14, fontWeight: 500 }}>
                  JWT Token
                </label>
                <input
                  id="token"
                  className="input"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="token para Authorization"
                />
              </div>
            </div>

            <button className="btn btn-primary" onClick={saveLocalConfig}>
              Guardar configuración
            </button>
          </section>
        </>
      )}

      {error && (
        <div className="card" style={{ padding: 24, backgroundColor: 'var(--danger-light)', border: '1px solid var(--danger)' }}>
          <p style={{ margin: 0, color: 'var(--danger)', fontWeight: 500 }}>{error}</p>
        </div>
      )}

    </main>
  )
}
