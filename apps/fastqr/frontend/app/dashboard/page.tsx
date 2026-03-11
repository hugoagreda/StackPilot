'use client'

import { useEffect, useState } from 'react'
import { api, type Overview } from '@/lib/api'
import { DashboardCard } from '@/components/DashboardCard'

export default function DashboardPage() {
  const [overview, setOverview] = useState<Overview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const restaurantId = localStorage.getItem('fastqr_restaurant_id')
    if (!restaurantId) {
      setError('Restaurante no configurado')
      setLoading(false)
      return
    }
    api
      .getOverview(restaurantId)
      .then(setOverview)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const today = new Date().toLocaleDateString('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Resumen</h1>
        <p className="mt-1 text-sm text-gray-500 capitalize">{today}</p>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-gray-400">
          <div className="w-5 h-5 border-2 border-orange-400 border-t-transparent rounded-full animate-spin" />
          Cargando...
        </div>
      )}

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {overview && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <DashboardCard
            label="Votos totales"
            value={overview.total_votes}
          />
          <DashboardCard
            label="Valoraciones"
            value={overview.total_feedback}
          />
          <DashboardCard
            label="Nota media"
            value={overview.avg_rating > 0 ? overview.avg_rating.toFixed(1) : '—'}
            sub="sobre 5"
          />
          <DashboardCard
            label="Sesiones únicas"
            value={overview.unique_sessions}
            sub="mesas visitadas"
          />
        </div>
      )}
    </div>
  )
}
