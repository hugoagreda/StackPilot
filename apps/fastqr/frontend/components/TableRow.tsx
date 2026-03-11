'use client'

import type { Table } from '@/lib/api'

interface TableRowProps {
  table: Table
  onDownloadQR: (table: Table) => void
}

export function TableRow({ table, onDownloadQR }: TableRowProps) {
  return (
    <div className="flex items-center justify-between bg-white rounded-xl px-5 py-4 shadow-sm border border-gray-100">
      <div>
        <p className="font-semibold text-gray-900">Mesa {table.code}</p>
      </div>
      <button
        onClick={() => onDownloadQR(table)}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-orange-500 text-white text-sm font-semibold
          hover:bg-orange-600 active:bg-orange-700 transition-colors"
      >
        ↓ Descargar QR
      </button>
    </div>
  )
}
