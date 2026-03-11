'use client'

import { useEffect, useState } from 'react'
import QRCode from 'qrcode'
import { api, type Table } from '@/lib/api'
import { TableRow } from '@/components/TableRow'

export default function DashboardTablesPage() {
  const [restaurantId, setRestaurantId] = useState<string | null>(null)
  const [tables, setTables] = useState<Table[]>([])
  const [newTableCode, setNewTableCode] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadTables = async (rid: string) => {
    const data = await api.getTables(rid)
    setTables(data)
  }

  useEffect(() => {
    const rid = localStorage.getItem('fastqr_restaurant_id')
    setRestaurantId(rid)
    if (!rid) {
      setError('Restaurante no encontrado')
      setLoading(false)
      return
    }
    loadTables(rid)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const handleCreateTable = async () => {
    if (!restaurantId || !newTableCode.trim()) return
    try {
      await api.createTable(restaurantId, newTableCode.trim())
      setNewTableCode('')
      await loadTables(restaurantId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear mesa')
    }
  }

  const downloadQR = async (table: Table) => {
    const url = `${window.location.origin}/t/${table.qr_token}`
    try {
      const dataUrl = await QRCode.toDataURL(url, {
        width: 720,
        margin: 2,
        color: {
          dark: '#111827',
          light: '#FFFFFF',
        },
      })

      const a = document.createElement('a')
      a.href = dataUrl
      a.download = `mesa-${table.code}.png`
      document.body.appendChild(a)
      a.click()
      a.remove()
    } catch {
      setError('No se pudo descargar el QR')
    }
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-gray-900">Mesas y códigos QR</h1>
        <p className="text-sm text-gray-500 mt-1">Crea mesas y descarga su QR para imprimir.</p>
      </header>

      <section className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
        <h2 className="font-semibold mb-3">Nueva mesa</h2>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            value={newTableCode}
            onChange={(e) => setNewTableCode(e.target.value)}
            placeholder="Ej: 12"
            className="flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm"
          />
          <button
            onClick={handleCreateTable}
            className="px-4 py-2 rounded-lg bg-orange-500 text-white text-sm font-semibold hover:bg-orange-600"
          >
            Crear mesa
          </button>
        </div>
      </section>

      {loading && <p className="text-sm text-gray-400">Cargando...</p>}
      {error && <p className="text-sm text-red-500">{error}</p>}

      <section className="space-y-3">
        {tables.map((table) => (
          <TableRow key={table.id} table={table} onDownloadQR={downloadQR} />
        ))}

        {!loading && tables.length === 0 && (
          <p className="text-sm text-gray-400">Aún no hay mesas creadas.</p>
        )}
      </section>
    </div>
  )
}
