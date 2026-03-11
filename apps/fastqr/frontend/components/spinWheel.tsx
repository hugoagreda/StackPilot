'use client'

import { useState } from 'react'
import { fastqrApi } from '@/lib/api'

interface SpinWheelProps {
  qrToken: string
  sessionToken: string
}

export function SpinWheel({ qrToken, sessionToken }: SpinWheelProps) {
  const [loading, setLoading] = useState(false)
  const [reward, setReward] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSpin = async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await fastqrApi.spinWheel(qrToken, sessionToken)

      setReward(result.reward_label)
    } catch (err) {
      setError('No se pudo girar la ruleta')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section
      className="card"
      style={{
        padding: 16,
        marginTop: 14,
        textAlign: 'center',
      }}
    >
      <h2 style={{ marginTop: 0 }}>🎁 Prueba tu suerte</h2>

      {!reward && (
        <>
          <p className="muted">
            Gira la ruleta y consigue un premio.
          </p>

          <button
            className="btn btn-primary"
            onClick={handleSpin}
            disabled={loading}
            style={{ marginTop: 10 }}
          >
            {loading ? 'Girando...' : 'Girar ruleta'}
          </button>
        </>
      )}

      {reward && (
        <div style={{ marginTop: 12 }}>
          <p
            style={{
              fontSize: 18,
              fontWeight: 600,
              margin: 0,
            }}
          >
            🎉 Has ganado
          </p>

          <p
            style={{
              fontSize: 20,
              marginTop: 6,
            }}
          >
            {reward}
          </p>
        </div>
      )}

      {error && (
        <p
          style={{
            color: 'var(--danger)',
            marginTop: 10,
          }}
        >
          {error}
        </p>
      )}
    </section>
  )
}