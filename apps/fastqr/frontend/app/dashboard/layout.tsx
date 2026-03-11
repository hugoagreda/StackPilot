'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'

const navItems = [
  { href: '/dashboard', label: 'Resumen', icon: '📊' },
  { href: '/dashboard/dishes', label: 'Carta', icon: '🍽️' },
  { href: '/dashboard/tables', label: 'Mesas', icon: '📱' },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      {/* Sidebar */}
      <aside className="w-full md:w-56 bg-white border-b md:border-b-0 md:border-r border-gray-100 flex md:flex-col md:h-screen md:sticky md:top-0">
        <div className="p-5 flex items-center md:mb-2">
          <span className="font-bold text-xl text-gray-900">FastQR</span>
        </div>

        <nav className="flex md:flex-col gap-1 px-3 pb-3 flex-1 overflow-x-auto md:overflow-x-visible">
          {navItems.map(({ href, label, icon }) => {
            const active = pathname === href
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors whitespace-nowrap
                  ${active
                    ? 'bg-orange-50 text-orange-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
              >
                <span>{icon}</span>
                {label}
              </Link>
            )
          })}
        </nav>

      </aside>

      {/* Content */}
      <main className="flex-1 p-6 md:p-8 overflow-y-auto">{children}</main>
    </div>
  )
}
