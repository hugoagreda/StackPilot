interface DashboardCardProps {
  label: string
  value: string | number
  sub?: string
}

export function DashboardCard({ label, value, sub }: DashboardCardProps) {
  return (
    <div 
      className="card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: 24,
        transition: 'all 0.2s ease',
      }}
    >
      <p className="text-sm muted" style={{ margin: 0 }}>
        {label}
      </p>
      <p 
        style={{ 
          marginTop: 8, 
          fontSize: 36, 
          fontWeight: 700, 
          margin: '8px 0 0 0',
          color: 'var(--primary)',
        }}
      >
        {value}
      </p>
      {sub && (
        <p className="text-xs muted" style={{ marginTop: 8, margin: '8px 0 0 0' }}>
          {sub}
        </p>
      )}
    </div>
  )
}
