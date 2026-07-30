import { Icon } from '../components/icons/Icon'
import {
  Cancel01Icon,
  Download04Icon,
  PlayIcon,
  RefreshIcon,
} from '@hugeicons/core-free-icons'
import type { Scene } from './data'

const BADGES = [
  { label: 'background generated', tone: 'border-warning/25 bg-warning/10 text-warning' },
  { label: 'product locked', tone: 'border-success/25 bg-success/10 text-success' },
  { label: 'type deterministic', tone: 'border-border-strong bg-elevated text-muted' },
]

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
  const tone = disabled
    ? 'cursor-not-allowed text-faint'
    : primary
      ? 'cursor-pointer text-accent hover:text-accent-hover'
      : 'cursor-pointer text-muted hover:text-foreground'
  return (
    <button
      disabled={disabled}
      className={`flex min-w-[76px] flex-col items-center gap-1.5 rounded-lg px-3 py-2 transition-colors ${tone}`}
    >
      <Icon icon={icon} size={19} />
      <span className="text-[12px] font-medium">{label}</span>
    </button>
  )
}

export function SceneCanvas({ scene, running }: { scene: Scene; running?: boolean }) {
  const blocked = scene.checks.some((c) => c.status === 'fail')

  return (
    <div className="flex min-w-0 flex-1 flex-col gap-3 px-6 py-5">
      <div className="flex min-h-0 flex-1 items-center justify-center">
        <img
          src={scene.still}
          alt={`${scene.label} scene`}
          className={`max-h-[62vh] rounded-2xl border shadow-2xl shadow-black/50 ${
            blocked ? 'border-danger/40' : 'border-border'
          }`}
        />
      </div>

      <div className="flex flex-wrap items-center justify-center gap-2">
        {blocked ? (
          <span className="rounded-full border border-danger/30 bg-danger/10 px-3 py-1 text-[12px] text-danger">
            Export withheld — the product no longer matches the approved asset
          </span>
        ) : (
          BADGES.map((badge) => (
            <span
              key={badge.label}
              className={`rounded-full border px-2.5 py-1 text-[11px] ${badge.tone}`}
            >
              {badge.label}
            </span>
          ))
        )}
      </div>

      <div className="flex items-center justify-center gap-1 rounded-2xl border border-border bg-surface/80 px-3 py-2">
        {running ? (
          <>
            <Action icon={PlayIcon} label="Preview" disabled />
            <Action icon={Cancel01Icon} label="Cancel" />
          </>
        ) : (
          <>
            <Action icon={RefreshIcon} label="Repair" />
            <Action icon={PlayIcon} label="Preview" />
            <Action
              icon={Download04Icon}
              label={blocked ? 'Blocked' : 'Export'}
              primary={!blocked}
              disabled={blocked}
            />
          </>
        )}
      </div>
    </div>
  )
}
