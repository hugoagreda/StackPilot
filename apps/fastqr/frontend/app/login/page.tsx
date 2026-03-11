'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { fastqrApi } from '@/lib/api'

export default function LoginPage() {
  const router = useRouter()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()

    setLoading(true)
    setError(null)

    try {
      const res = await fastqrApi.login(email, password)

      /* guardar token */
      localStorage.setItem('fastqr_token', res.access_token)
      localStorage.setItem('fastqr_restaurant_id', res.restaurant_id)

      /* guardar cookie para middleware */
      document.cookie = `fastqr_token=${res.access_token}; path=/; max-age=86400`

      router.push('/dashboard')
    } catch (err) {
      setError('Credenciales incorrectas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="shell" style={{ paddingTop: 60 }}>
      <section
        className="card"
        style={{
          maxWidth: 420,
          margin: '0 auto',
          padding: 20,
        }}
      >
        <h1 style={{ marginTop: 0 }}>Login</h1>

        <p className="muted" style={{ marginTop: 6 }}>
          Accede al panel de tu restaurante.
        </p>

        <form
          onSubmit={handleLogin}
          className="stack"
          style={{ marginTop: 16 }}
        >
          <div>
            <label>Email</label>
            <input
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label>Password</label>
            <input
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <p style={{ color: 'var(--danger)', margin: 0 }}>
              {error}
            </p>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </section>
    </main>
  )
}