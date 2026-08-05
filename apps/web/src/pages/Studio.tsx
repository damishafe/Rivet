import { useState } from 'react'
import { Sidebar } from '../studio/Sidebar'
import { SceneCanvas } from '../studio/SceneCanvas'
import { AuditPanel } from '../studio/AuditPanel'
import { StageMonitor } from '../studio/StageMonitor'
import { BLOCKED_SCENE, SCENES } from '../studio/data'
import type { Scene } from '../studio/data'

export type Mode = 'running' | 'verified' | 'blocked'

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
    <div className="studio-app flex h-screen min-h-[640px] items-stretch p-2 text-foreground sm:p-3">
      <div className="studio-frame flex min-h-0 flex-1 overflow-hidden rounded-[22px] border border-white/[0.07] bg-[#09090b]/95 shadow-[0_28px_100px_rgba(0,0,0,0.65)]">
        <Sidebar
          scenes={scenes}
          activeId={activeId}
          onSelect={setActiveId}
          mode={mode}
          modes={MODES}
          onModeSelect={select}
        />

        <main className="min-w-0 flex-1 border-l border-white/[0.06]">
          <SceneCanvas
            scene={scene}
            running={mode === 'running'}
            onGenerate={() => select('running')}
          />
        </main>

        <aside className="hidden w-[336px] shrink-0 border-l border-white/[0.06] bg-[#0b0b0e] xl:block">
          {mode === 'running' ? <StageMonitor /> : <AuditPanel scene={scene} />}
        </aside>
      </div>
    </div>
  )
}
