import { Icon } from '../components/icons/Icon'
import { Cancel01Icon, Download04Icon, PlayIcon, RefreshIcon } from '@hugeicons/core-free-icons'
import type { Scene } from './data'

const LAYER_BADGES = [
  { label: 'background · generated', tone: 'generated' },
  { label: 'product · locked', tone: 'locked' },
  { label: 'logo · locked', tone: 'locked' },
  { label: 'type · deterministic', tone: 'deterministic' },
] as const

const TONES: Record<string, string> = {
  generated: 'border-warning/30 bg-warning/10 text-warning',
  locked: 'border-success/30 bg-success/10 text-success',
  deterministic: 'border-border-strong bg-elevated text-muted',
}

function Action({
  icon,
  label,
  primary,
  disabled,
}: {
  icon: typeof PlayIcon
  label: string
  primary?: boolean
  disabled?: boolean
}) {
  const base =
    'flex items-center gap-2 rounded-lg px-3.5 py-2 text-[12px] font-medium transition-colors'
  if (disabled) {
    return (
      <span className={`${base} cursor-not-allowed border border-border text-faint`}>
        <Icon icon={icon} size={14} />
        {label}
      </span>
    )
  }
  return (
    <button
      className={
        primary
          ? `${base} cursor-pointer bg-accent text-accent-fg hover:bg-accent-hover`
          : `${base} cursor-pointer border border-border text-muted hover:border-border-strong hover:text-foreground`
      }
    >
      <Icon icon={icon} size={14} />
      {label}
    </button>
  )
}

export function SceneCanvas({ scene, running }: { scene: Scene; running?: boolean }) {
  const blocked = scene.checks.some((c) => c.status === 'fail')

  return (
    <div className="flex min-w-0 flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-border px-6 py-3">
        <div>
          <h1 className="font-display text-[14px] font-medium tracking-tight text-foreground">
            {scene.label}
          </h1>
          <p className="text-[11px] text-faint">{scene.purpose}</p>
        </div>
        <div className="flex flex-wrap justify-end gap-1.5">
          {LAYER_BADGES.map((badge) => (
            <span
              key={badge.label}
              className={`rounded-full border px-2 py-0.5 font-mono text-[9px] ${TONES[badge.tone]}`}
            >
              {badge.label}
            </span>
          ))}
        </div>
      </div>

      <div className="flex min-h-0 flex-1 items-center justify-center overflow-auto bg-background p-6">
        <figure className="relative">
          <img
            src={scene.still}
            alt={`${scene.label} scene`}
            className="max-h-[62vh] rounded-xl border border-border"
          />
          {blocked && (
            <figcaption className="absolute inset-x-0 bottom-0 rounded-b-xl border-t border-danger/40 bg-danger/15 px-3 py-2 text-center font-mono text-[10px] text-danger backdrop-blur-sm">
              export withheld — A01 lineage mismatch
            </figcaption>
          )}
        </figure>
      </div>

      <div className="border-t border-border px-6 py-3">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <dl className="min-w-0 space-y-1">
            <div className="flex gap-2 text-[12px]">
              <dt className="w-[52px] shrink-0 text-faint">headline</dt>
              <dd className="truncate text-foreground">{scene.headline}</dd>
            </div>
            <div className="flex gap-2 text-[12px]">
              <dt className="w-[52px] shrink-0 text-faint">support</dt>
              <dd className="truncate text-muted">{scene.support}</dd>
            </div>
            <div className="flex gap-2 text-[12px]">
              <dt className="w-[52px] shrink-0 text-faint">spoken</dt>
              <dd className="truncate text-muted">{scene.narration}</dd>
            </div>
          </dl>
          <div className="flex shrink-0 gap-2">
            {running ? (
              <>
                <Action icon={PlayIcon} label="Preview" disabled />
                <Action icon={Cancel01Icon} label="Cancel run" />
              </>
            ) : (
              <>
                <Action icon={RefreshIcon} label="Repair" />
                <Action icon={PlayIcon} label="Preview" />
                {blocked ? (
                  <Action icon={Download04Icon} label="Export blocked" disabled />
                ) : (
                  <Action icon={Download04Icon} label="Export pack" primary />
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
