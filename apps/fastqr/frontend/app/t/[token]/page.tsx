'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { fastqrApi, type PublicMenu } from '@/lib/api'
import { MenuList } from '@/components/MenuList'
import { SpinWheel } from '@/components/SpinWheel'

function getOrCreateSessionToken(qrToken: string) {
  const key = `fastqr_session_${qrToken}`
  const current = sessionStorage.getItem(key)

  if (current) return current

  const created = crypto.randomUUID()
  sessionStorage.setItem(key, created)

  return created
}

function getVotedMap(qrToken: string) {
  const key = `fastqr_voted_${qrToken}`
  const raw = sessionStorage.getItem(key)

  return new Set<string>(raw ? JSON.parse(raw) : [])
}

function saveVoted(qrToken: string, dishId: string, list: Set<string>) {
  const updated = new Set(list)

  updated.add(dishId)

  sessionStorage.setItem(
    `fastqr_voted_${qrToken}`,
    JSON.stringify(Array.from(updated))
  )

  return updated
}

export default function TablePage() {
  const params = useParams<{ token: string }>()
  const token = params.token

  const [menu, setMenu] = useState<PublicMenu | null>(null)
  const [sessionToken, setSessionToken] = useState('')
  const [votedDishes, setVotedDishes] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return

    const session = getOrCreateSessionToken(token)

    setSessionToken(session)
    setVotedDishes(getVotedMap(token))

    fastqrApi
      .getMenu(token, session)
      .then(setMenu)
      .catch((e) =>
        setError(e instanceof Error ? e.message : 'No se pudo cargar menu')
      )
      .finally(() => setLoading(false))
  }, [token])

  const handleVote = async (dishId: string) => {
    if (!token || !sessionToken || votedDishes.has(dishId)) return

    try {
      await fastqrApi.voteDish(token, dishId, sessionToken)

      setVotedDishes((prev) => saveVoted(token, dishId, prev))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo votar')
    }
  }

  if (loading) {
    return (
      <main className="shell section">
        <div className="card" style={{ textAlign: 'center' }}>
          <p className="muted" style={{ margin: 0 }}>
            Cargando menú...
          </p>
        </div>
      </main>
    )
  }

  if (error || !menu) {
    return (
      <main className="shell section">
        <div className="card">
          <h1 style={{ marginTop: 0 }}>Menú no disponible</h1>

          <p className="muted" style={{ marginBottom: 0 }}>
            {error ?? 'No se encontró el token de la mesa.'}
          </p>
        </div>
      </main>
    )
  }

  return (
    <main
      className="shell"
      style={{
        maxWidth: 640,
        padding: '18px 0 32px',
      }}
    >
      {/* HEADER */}

      <header
        className="card"
        style={{
          padding: 18,
          marginBottom: 16,
        }}
      >
        <p
          className="muted"
          style={{
            margin: 0,
            fontSize: 14,
          }}
        >
          Mesa {menu.table}
        </p>

        <h1
          style={{
            margin: '6px 0 0',
            fontSize: 26,
            fontWeight: 700,
          }}
        >
          {menu.restaurant}
        </h1>
      </header>

      {/* MENU */}

      <MenuList
        categories={menu.categories}
        votedDishes={votedDishes}
        onVote={handleVote}
      />

      {/* SPIN WHEEL */}

      <SpinWheel
        qrToken={token}
        sessionToken={sessionToken}
      />
    </main>
  )
}