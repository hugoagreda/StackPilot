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
            position: 'sticky',
            top: 0,
            zIndex: 50,
          }}
        >
          <div
            className="shell"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '16px 0',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{
                width: 32,
                height: 32,
                background: 'linear-gradient(135deg, var(--primary), var(--primary-hover))',
                borderRadius: 'var(--radius)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 700,
                fontSize: 16,
              }}>
                QR
              </div>
              <span style={{ fontWeight: 600, color: 'var(--text)' }}>FastQR</span>
            </div>

            <nav style={{ display: 'flex', gap: 24 }}>
              <a 
                className="muted" 
                href="/" 
                style={{ textDecoration: 'none', transition: 'color 0.2s ease', fontSize: 14 }}
                onMouseOver={(e) => (e.currentTarget.style.color = 'var(--text)')}
                onMouseOut={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
              >
                Inicio
              </a>

              <a 
                className="muted" 
                href="/dashboard" 
                style={{ textDecoration: 'none', transition: 'color 0.2s ease', fontSize: 14 }}
                onMouseOver={(e) => (e.currentTarget.style.color = 'var(--text)')}
                onMouseOut={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
              >
                Dashboard
              </a>
            </nav>
          </div>
        </header>

        <div
          className="shell"
          style={{
            paddingTop: 40,
            paddingBottom: 60,
          }}
        >
          {children}
        </div>

      </body>
    </html>
  )
}
