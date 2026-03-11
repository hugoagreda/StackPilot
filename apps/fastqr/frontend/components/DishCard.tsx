'use client'

import { VoteButton } from './VoteButton'

export interface DishCardProps {
  id: string
  name: string
  description?: string
  price_cents: number
  image_url?: string
  voted: boolean
  votingDisabled?: boolean
  onVote: (dishId: string) => void
}

export function DishCard({
  id,
  name,
  description,
  price_cents,
  image_url,
  voted,
  votingDisabled,
  onVote,
}: DishCardProps) {

  const price = (price_cents / 100).toLocaleString('es-ES', {
    style: 'currency',
    currency: 'EUR',
  })

  return (
    <article
      className="card"
      style={{
        padding: 16,
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
      }}
    >

      {image_url && (
        <img
          src={image_url}
          alt={name}
          style={{
            width: '100%',
            height: 160,
            objectFit: 'cover',
            borderRadius: 10,
            marginBottom: 4,
          }}
        />
      )}

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'start',
          gap: 10,
        }}
      >
        <h3
          style={{
            margin: 0,
            fontSize: 17,
            fontWeight: 600,
          }}
        >
          {name}
        </h3>

        <strong
          style={{
            fontSize: 15,
            color: 'var(--primary)',
            whiteSpace: 'nowrap',
          }}
        >
          {price}
        </strong>
      </div>

      {description && (
        <p
          className="muted"
          style={{
            margin: 0,
            fontSize: 14,
            lineHeight: 1.4,
          }}
        >
          {description}
        </p>
      )}

      <div style={{ marginTop: 6 }}>
        <VoteButton
          voted={voted}
          disabled={votingDisabled}
          onClick={() => onVote(id)}
        />
      </div>

    </article>
  )
}