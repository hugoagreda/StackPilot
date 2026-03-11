'use client'

import type { Table } from '@/lib/api'

interface QRTableCardProps {
  table: Table
  onDownloadQR: (table: Table) => void
}

export function QRTableCard({ table, onDownloadQR }: QRTableCardProps) {
  return (
    <article className="card" style={{ padding: 14 }}>
      <p style={{ margin: 0, fontWeight: 700 }}>Mesa {table.code}</p>
      <p className="muted" style={{ margin: '6px 0 10px', fontSize: 13 }}>
        Token: {table.qr_token}
      </p>
      <button className="btn btn-primary" onClick={() => onDownloadQR(table)}>
        Descargar QR
      </button>
    </article>
  )
}