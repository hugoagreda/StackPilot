'use client'

interface VoteButtonProps {
  voted: boolean
  disabled?: boolean
  onClick: () => void
}

export function VoteButton({ voted, disabled, onClick }: VoteButtonProps) {
  if (voted) {
    return (
      <p className="mt-3 text-sm font-medium text-green-600 flex items-center gap-1">
        ✓ Voto registrado
      </p>
    )
  }
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="mt-3 w-full py-2 rounded-lg bg-orange-500 text-white text-sm font-semibold
        hover:bg-orange-600 active:bg-orange-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
    >
      👍 Votar
    </button>
  )
}
