import { STAGES, RECEIPT } from './data'

const DOT: Record<string, string> = {
  done: 'bg-success',
  running: 'bg-accent shadow-[0_0_10px_rgba(255,59,0,0.6)] animate-pulse',
  queued: 'bg-white/15',
}

export function StageMonitor() {
  const done = STAGES.filter((stage) => stage.state === 'done')
  const elapsed = done.reduce((total, stage) => total + stage.seconds, 0)
  const progress = Math.round((done.length / STAGES.length) * 100)

  return (
    <div className="flex h-full flex-col">
      <header className="flex h-[68px] shrink-0 items-center justify-between border-b border-white/[0.06] px-4">
        <div>
          <h2 className="font-display text-[13px] font-medium tracking-[-0.01em] text-foreground">
            Generation run
          </h2>
          <p className="mt-1 text-[9px] text-faint">Campaign pipeline · live</p>
        </div>
        <span className="flex items-center gap-1.5 rounded-full border border-accent/20 bg-accent/10 px-2 py-1 text-[8px] font-medium text-accent">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
          RUNNING
        </span>
      </header>

      <div className="border-b border-white/[0.06] p-4">
        <div className="flex items-end justify-between">
          <div>
            <span className="font-display text-[28px] font-medium tracking-[-0.04em] text-foreground">
              {progress}%
            </span>
            <span className="ml-2 text-[9px] text-faint">complete</span>
          </div>
          <span className="font-mono text-[9px] text-muted">{elapsed.toFixed(1)}s</span>
        </div>
        <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/[0.07]">
          <div
            className="h-full rounded-full bg-accent shadow-[0_0_12px_rgba(255,59,0,0.5)] transition-[width] duration-700"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2">
          <div className="rounded-xl bg-white/[0.03] p-2.5">
            <p className="text-[8px] uppercase tracking-[0.12em] text-faint">Peak VRAM</p>
            <p className="mt-1 font-mono text-[11px] text-muted">{RECEIPT.peakVramMb} MB</p>
          </div>
          <div className="rounded-xl bg-white/[0.03] p-2.5">
            <p className="text-[8px] uppercase tracking-[0.12em] text-faint">Stages</p>
            <p className="mt-1 font-mono text-[11px] text-muted">{done.length} / {STAGES.length}</p>
          </div>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-2">
        {STAGES.map((stage) => (
          <div key={stage.name} className="flex items-center gap-3 border-b border-white/[0.045] py-2.5 last:border-0">
            <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${DOT[stage.state]}`} />
            <span className={`min-w-0 flex-1 truncate font-mono text-[9px] ${
              stage.state === 'queued' ? 'text-faint' : 'text-muted'
            }`}>
              {stage.name}
            </span>
            <span className="shrink-0 font-mono text-[8px] text-faint">
              {stage.state === 'queued' ? 'QUEUED' : stage.state === 'running' ? 'RUNNING' : `${stage.seconds.toFixed(2)}s`}
            </span>
          </div>
        ))}
      </div>

      <footer className="shrink-0 border-t border-white/[0.06] px-4 py-3">
        <p className="font-mono text-[8px] leading-relaxed text-faint">
          One heavy model resident at a time · VRAM recycled between stages
        </p>
      </footer>
    </div>
  )
}
