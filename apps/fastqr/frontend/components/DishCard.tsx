'use client'

import Image from 'next/image'
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
    <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100">
      {image_url && (
        <div className="relative w-full h-40">
          <Image
            src={image_url}
            alt={name}
            fill
            className="object-cover"
            sizes="(max-width: 640px) 100vw, 50vw"
          />
        </div>
      )}
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <h3 className="font-semibold text-gray-900 leading-snug">{name}</h3>
          <span className="shrink-0 text-sm font-semibold text-gray-700">{price}</span>
        </div>
        {description && (
          <p className="mt-1 text-sm text-gray-500 line-clamp-2">{description}</p>
        )}
        <VoteButton voted={voted} disabled={votingDisabled} onClick={() => onVote(id)} />
      </div>
    </div>
  )
}
