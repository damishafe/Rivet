import { Link } from 'react-router-dom'

export default function Studio() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background">
      <div className="rounded-xl border border-border bg-surface px-8 py-6 text-center">
        <img src="/logo.png" alt="Rivet" className="w-12 h-12 rounded-full object-cover mx-auto mb-4" />
        <h1 className="text-lg font-semibold tracking-tight text-foreground">Rivet Studio</h1>
        <p className="mt-1 text-sm text-muted">The creation flow lands here — reference-first, coming with D10 polish.</p>
        <p className="mt-3 font-mono text-xs text-faint">v0.1.0 · scaffold</p>
        <Link to="/" className="mt-4 inline-block font-mono text-xs text-accent hover:text-foreground transition-colors">
          ← BACK TO LANDING
        </Link>
      </div>
    </main>
  )
}
