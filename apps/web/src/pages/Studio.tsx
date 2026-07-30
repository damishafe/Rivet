import { useState } from 'react'
import { Sidebar } from '../studio/Sidebar'
import { SceneCanvas } from '../studio/SceneCanvas'
import { AuditPanel } from '../studio/AuditPanel'
import { StageMonitor } from '../studio/StageMonitor'
import { BLOCKED_SCENE, SCENES } from '../studio/data'
import type { Scene } from '../studio/data'

type Mode = 'running' | 'verified' | 'blocked'

const MODES: { id: Mode; label: string }[] = [
  { id: 'running', label: 'Generating' },
  { id: 'verified', label: 'Verified' },
  { id: 'blocked', label: 'Tampered' },
]

function initialMode(): Mode {
  const hash = window.location.hash.replace('#', '')
  return MODES.some((option) => option.id === hash) ? (hash as Mode) : 'verified'
}

export default function Studio() {
  const [mode, setMode] = useState<Mode>(initialMode)
  const [activeId, setActiveId] = useState<Scene['id']>('hook')

  const select = (next: Mode) => {
    setMode(next)
    window.location.hash = next
  }

  const scenes =
    mode === 'blocked'
      ? SCENES.map((s) => ({ ...s, still: BLOCKED_SCENE.still, checks: BLOCKED_SCENE.checks }))
      : SCENES
  const scene = scenes.find((s) => s.id === activeId) ?? scenes[0]

  return (
    <div className="flex h-screen items-stretch bg-gradient-to-br from-[#0a0a0d] via-background to-[#0d0a10] p-4 text-foreground">
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-border bg-background/80 shadow-2xl shadow-black/60 backdrop-blur">
      <div className="flex items-center gap-3 border-b border-border px-5 py-3">
        <span className="text-[12px] text-faint">State</span>
        <div className="flex gap-1">
          {MODES.map((option) => (
            <button
              key={option.id}
              onClick={() => select(option.id)}
              className={`cursor-pointer rounded-full border px-3 py-1 text-[12px] transition-colors ${
                mode === option.id
                  ? 'border-border-strong bg-elevated text-foreground'
                  : 'border-transparent text-faint hover:text-muted'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
        <p className="ml-auto hidden truncate font-mono text-[11px] text-faint md:block">
          Radeon PRO W7900 · 67.8s cold · 27/27 checks
        </p>
      </div>

      <div className="flex min-h-0 flex-1">
        <Sidebar scenes={scenes} activeId={activeId} onSelect={setActiveId} />
        <SceneCanvas scene={scene} running={mode === 'running'} />
        <div className="w-[330px] shrink-0 border-l border-border">
          {mode === 'running' ? <StageMonitor /> : <AuditPanel scene={scene} />}
        </div>
      </div>
      </div>
    </div>
  )
}
