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
    <div className="flex h-screen flex-col overflow-hidden bg-background text-foreground">
      <div className="flex items-center gap-3 border-b border-border bg-surface px-4 py-2">
        <span className="font-mono text-[10px] uppercase tracking-wider text-faint">state</span>
        <div className="flex gap-1">
          {MODES.map((option) => (
            <button
              key={option.id}
              onClick={() => select(option.id)}
              className={`cursor-pointer rounded-full border px-2.5 py-0.5 font-mono text-[10px] transition-colors ${
                mode === option.id
                  ? 'border-border-strong bg-elevated text-foreground'
                  : 'border-transparent text-faint hover:text-muted'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
        <p className="ml-auto hidden truncate font-mono text-[10px] text-faint sm:block">
          Radeon PRO W7900 · 67.8s cold · 27/27 checks
        </p>
      </div>

      <div className="flex min-h-0 flex-1">
        <Sidebar scenes={scenes} activeId={activeId} onSelect={setActiveId} />
        <SceneCanvas scene={scene} running={mode === 'running'} />
        <div className="w-[320px] shrink-0 border-l border-border bg-surface">
          {mode === 'running' ? <StageMonitor /> : <AuditPanel scene={scene} />}
        </div>
      </div>
    </div>
  )
}
