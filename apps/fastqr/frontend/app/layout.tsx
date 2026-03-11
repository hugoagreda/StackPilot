import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'FastQR',
  description: 'Menu digital para restaurantes',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body>

        <header
          style={{
            borderBottom: '1px solid var(--line)',
            background: 'var(--surface)',
          }}
        >
          <div
            className="shell"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '14px 0',
              fontWeight: 600,
            }}
          >
            <span>FastQR</span>

            <nav style={{ display: 'flex', gap: 14 }}>
              <a className="muted" href="/">
                Inicio
              </a>

              <a className="muted" href="/dashboard">
                Dashboard
              </a>
            </nav>
          </div>
        </header>

        <main
          className="shell"
          style={{
            paddingTop: 32,
            paddingBottom: 40,
          }}
        >
          {children}
        </main>

      </body>
    </html>
  )
}