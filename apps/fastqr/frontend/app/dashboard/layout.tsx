'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'

const navItems = [
  { href: '/dashboard', label: 'Overview' },
  { href: '/dashboard/dishes', label: 'Dishes' },
  { href: '/dashboard/tables', label: 'Tables' },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="shell" style={{ padding: '14px 0 24px' }}>
      <header className="card" style={{ padding: 12, marginBottom: 12 }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 10,
            flexWrap: 'wrap',
          }}
        >
          <strong>FastQR Dashboard</strong>
          <nav style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {navItems.map(({ href, label }) => {
            const active = pathname === href
            return (
              <Link
                key={href}
                href={href}
                className={`btn ${active ? 'btn-primary' : 'btn-soft'}`}
                style={{ padding: '8px 12px' }}
              >
                {label}
              </Link>
            )
          })}
          </nav>
        </div>
      </header>
      <main>{children}</main>
    </div>
  )
}
