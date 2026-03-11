'use client'

interface VoteButtonProps {
  voted: boolean
  disabled?: boolean
  onClick: () => void
}

export function VoteButton({ voted, disabled, onClick }: VoteButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || voted}
      className="btn"
      style={{
        width: '100%',
        background: voted ? '#e6f7ef' : 'var(--primary)',
        color: voted ? 'var(--ok)' : '#fff',
        border: voted ? '1px solid #b7e4c7' : 'none',
        fontWeight: 600,
      }}
    >
      {voted ? '✓ Voto registrado' : '👍 Votar'}
    </button>
  )
}