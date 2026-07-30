import { STAGES } from './data'
import { RECEIPT } from './data'

const DOT: Record<string, string> = {
  done: 'bg-success',
  running: 'bg-accent animate-pulse-fast',
  queued: 'bg-border-strong',
}

export function StageMonitor() {
  const done = STAGES.filter((s) => s.state === 'done')
  const elapsed = done.reduce((total, stage) => total + stage.seconds, 0)
  const progress = Math.round((done.length / STAGES.length) * 100)

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border px-4 py-3.5">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-[13px] font-medium tracking-tight text-foreground">
            Generation
          </h2>
          <span className="font-mono text-[10px] text-muted">{progress}%</span>
        </div>
        <div className="mt-2 h-1 overflow-hidden rounded-full bg-elevated">
          <div className="h-full rounded-full bg-accent" style={{ width: `${progress}%` }} />
        </div>
        <div className="mt-2 flex justify-between font-mono text-[10px] text-faint">
          <span>{elapsed.toFixed(1)}s elapsed</span>
          <span>peak {RECEIPT.peakVramMb} MB</span>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {STAGES.map((stage) => (
          <div
            key={stage.name}
            className="flex items-center gap-2.5 border-b border-border/60 px-4 py-2 last:border-0"
          >
            <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${DOT[stage.state]}`} />
            <span
              className={`flex-1 truncate font-mono text-[11px] ${
                stage.state === 'queued' ? 'text-faint' : 'text-foreground'
              }`}
            >
              {stage.name}
            </span>
            <span className="shrink-0 font-mono text-[10px] text-muted">
              {stage.state === 'queued' ? '—' : `${stage.seconds.toFixed(2)}s`}
            </span>
            <span className="w-[62px] shrink-0 text-right font-mono text-[10px] text-faint">
              {stage.vramMb === null ? 'n/a' : `${stage.vramMb} MB`}
            </span>
          </div>
        ))}
      </div>

      <div className="border-t border-border px-4 py-3">
        <p className="font-mono text-[10px] leading-relaxed text-faint">
          Peak VRAM is a per-stage maximum from torch.cuda.max_memory_allocated, reset before each
          stage. One heavy model is resident at a time.
        </p>
      </div>
    </div>
  )
}
