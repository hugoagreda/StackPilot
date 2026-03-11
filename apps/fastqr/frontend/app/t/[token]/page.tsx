'use client'

import { useEffect, useState, useCallback } from 'react'
import { useParams } from 'next/navigation'
import { api, type PublicMenu, type TodayRanking } from '@/lib/api'
import { MenuList } from '@/components/MenuList'

function getOrCreateSessionToken(qrToken: string): string {
  const key = `fastqr_session_${qrToken}`
  if (typeof window === 'undefined') return ''
  const existing = sessionStorage.getItem(key)
  if (existing) return existing
  const newToken = crypto.randomUUID()
  sessionStorage.setItem(key, newToken)
  return newToken
}

function getVotedDishes(qrToken: string): Set<string> {
  try {
    const key = `fastqr_voted_${qrToken}`
    const raw = sessionStorage.getItem(key)
    return new Set(raw ? JSON.parse(raw) : [])
  } catch {
    return new Set()
  }
}

function saveVotedDish(qrToken: string, dishId: string, current: Set<string>): Set<string> {
  const updated = new Set(current)
  updated.add(dishId)
  sessionStorage.setItem(`fastqr_voted_${qrToken}`, JSON.stringify([...updated]))
  return updated
}

interface StarRatingProps {
  value: number
  onChange: (v: number) => void
}

function StarRating({ value, onChange }: StarRatingProps) {
  return (
    <div className="flex gap-2">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => onChange(star)}
          className={`text-2xl transition-transform hover:scale-110 ${
            star <= value ? 'text-yellow-400' : 'text-gray-300'
          }`}
          aria-label={`${star} estrellas`}
        >
          ★
        </button>
      ))}
    </div>
  )
}

export default function TablePage() {
  const params = useParams<{ token: string }>()
  const token = params?.token ?? ''

  const [menu, setMenu] = useState<PublicMenu | null>(null)
  const [ranking, setRanking] = useState<TodayRanking | null>(null)
  const [votedDishes, setVotedDishes] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Feedback state
  const [feedbackRating, setFeedbackRating] = useState(0)
  const [feedbackComment, setFeedbackComment] = useState('')
  const [feedbackSent, setFeedbackSent] = useState(false)
  const [feedbackSending, setFeedbackSending] = useState(false)
  const [feedbackError, setFeedbackError] = useState<string | null>(null)

  const sessionToken = typeof window !== 'undefined' ? getOrCreateSessionToken(token) : ''

  const loadMenu = useCallback(async () => {
    if (!token) return
    try {
      const data = await api.getMenu(token, sessionToken)
      setMenu(data)
      setVotedDishes(getVotedDishes(token))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo cargar el menú')
    } finally {
      setLoading(false)
    }
  }, [token, sessionToken])

  const loadRanking = useCallback(async () => {
    if (!token) return
    try {
      const data = await api.getRanking(token)
      setRanking(data)
    } catch {
      // ranking is non-critical
    }
  }, [token])

  useEffect(() => {
    if (!token) return
    loadMenu()
    loadRanking()
  }, [loadMenu, loadRanking])

  const handleVote = async (dishId: string) => {
    if (votedDishes.has(dishId)) return
    try {
      await api.vote(token, dishId, sessionToken)
      setVotedDishes((prev) => saveVotedDish(token, dishId, prev))
      loadRanking()
    } catch (err) {
      console.error('Vote failed', err)
    }
  }

  const handleFeedback = async () => {
    if (feedbackRating === 0 || feedbackSending) return
    setFeedbackSending(true)
    setFeedbackError(null)
    try {
      await api.submitFeedback(
        token,
        feedbackRating,
        feedbackComment.trim() || undefined,
        sessionToken,
      )
      setFeedbackSent(true)
    } catch (err) {
      setFeedbackError(err instanceof Error ? err.message : 'Error al enviar')
    } finally {
      setFeedbackSending(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error || !menu) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="text-center">
          <p className="text-4xl mb-4">🍽️</p>
          <p className="text-gray-500">{error ?? 'Menú no disponible'}</p>
        </div>
      </div>
    )
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-8 pb-16">
      {/* Header */}
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900">{menu.restaurant}</h1>
        <p className="mt-1 text-gray-500">Mesa {menu.table}</p>
      </header>

      {/* Menu */}
      <MenuList categories={menu.categories} votedDishes={votedDishes} onVote={handleVote} />

      {/* Ranking */}
      {ranking && ranking.ranking.length > 0 && (
        <section className="mt-12">
          <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            🏆 Lo más votado hoy
          </h2>
          <ol className="space-y-2">
            {ranking.ranking.slice(0, 5).map((entry, i) => (
              <li
                key={entry.dish_id}
                className="flex items-center justify-between bg-white rounded-xl px-4 py-3 shadow-sm border border-gray-100"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`text-lg font-bold w-6 text-center ${
                      i === 0
                        ? 'text-yellow-400'
                        : i === 1
                          ? 'text-gray-400'
                          : i === 2
                            ? 'text-orange-600'
                            : 'text-gray-300'
                    }`}
                  >
                    {i + 1}
                  </span>
                  <span className="font-medium text-gray-800">{entry.dish_name}</span>
                </div>
                <span className="text-sm text-gray-500">{entry.votes} votos</span>
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* Feedback */}
      <section className="mt-12 bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-bold text-gray-800 mb-1">¿Cómo fue tu experiencia?</h2>
        <p className="text-sm text-gray-500 mb-4">Tu opinión ayuda al restaurante a mejorar.</p>

        {feedbackSent ? (
          <p className="text-green-600 font-semibold text-center py-4">
            ✓ ¡Gracias por tu valoración!
          </p>
        ) : (
          <div className="space-y-4">
            <StarRating value={feedbackRating} onChange={setFeedbackRating} />
            <textarea
              value={feedbackComment}
              onChange={(e) => setFeedbackComment(e.target.value)}
              placeholder="Comentario opcional..."
              rows={2}
              maxLength={800}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm resize-none
                focus:outline-none focus:ring-2 focus:ring-orange-400"
            />
            {feedbackError && <p className="text-sm text-red-500">{feedbackError}</p>}
            <button
              onClick={handleFeedback}
              disabled={feedbackRating === 0 || feedbackSending}
              className="w-full py-2.5 rounded-lg bg-orange-500 text-white font-semibold
                hover:bg-orange-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {feedbackSending ? 'Enviando...' : 'Enviar valoración'}
            </button>
          </div>
        )}
      </section>
    </main>
  )
}
