import { Link } from 'react-router-dom'
import { Icon } from '../components/icons/Icon'
import {
  ArrowLeft01Icon,
  CheckmarkCircle02Icon,
  ImageAdd02Icon,
  PaintBoardIcon,
  ShieldKeyIcon,
  SparklesIcon,
} from '@hugeicons/core-free-icons'
import type { Scene } from './data'
import { RECEIPT } from './data'

const STEPS = [
  { label: 'Project', icon: ImageAdd02Icon, done: true },
  { label: 'Brand DNA', icon: PaintBoardIcon, done: true },
  { label: 'Storyboard', icon: SparklesIcon, done: true },
  { label: 'Review + Verify', icon: ShieldKeyIcon, done: false, current: true },
]

type Props = {
  scenes: Scene[]
  activeId: string
  onSelect: (id: Scene['id']) => void
}

export function Sidebar({ scenes, activeId, onSelect }: Props) {
  return (
    <aside className="flex w-[236px] shrink-0 flex-col border-r border-border bg-surface">
      <div className="flex items-center gap-2.5 px-4 py-4">
        <img src="/logo.png" alt="" className="h-6 w-6 rounded-full object-cover" />
        <span className="font-display text-[13px] font-semibold tracking-tight text-foreground">
          Rivet
        </span>
        <Link
          to="/"
          className="ml-auto cursor-pointer text-faint transition-colors hover:text-foreground"
          aria-label="Back to landing"
        >
          <Icon icon={ArrowLeft01Icon} size={15} />
        </Link>
      </div>

      <div className="px-3">
        <p className="px-1 pb-1.5 font-mono text-[10px] uppercase tracking-wider text-faint">
          Kora Arc
        </p>
        {STEPS.map((step) => (
          <div
            key={step.label}
            className={`flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-[12px] ${
              step.current ? 'bg-elevated text-foreground' : 'text-muted'
            }`}
          >
            <Icon icon={step.icon} size={15} className={step.current ? '' : 'text-faint'} />
            <span className="flex-1 truncate">{step.label}</span>
            {step.done && <Icon icon={CheckmarkCircle02Icon} size={13} className="text-success" />}
          </div>
        ))}
      </div>

      <div className="mt-5 px-3">
        <p className="px-1 pb-1.5 font-mono text-[10px] uppercase tracking-wider text-faint">
          Scenes
        </p>
        {scenes.map((scene) => {
          const active = scene.id === activeId
          const failing = scene.checks.some((c) => c.status === 'fail')
          return (
            <button
              key={scene.id}
              onClick={() => onSelect(scene.id)}
              className={`flex w-full cursor-pointer items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-[12px] transition-colors ${
                active ? 'bg-elevated text-foreground' : 'text-muted hover:text-foreground'
              }`}
            >
              <img
                src={scene.still}
                alt=""
                className="h-7 w-[18px] shrink-0 rounded border border-border object-cover"
              />
              <span className="flex-1 truncate">{scene.label}</span>
              <span
                className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                  failing ? 'bg-danger' : 'bg-success'
                }`}
              />
            </button>
          )
        })}
      </div>

      <div className="mt-auto border-t border-border p-3">
        <p className="font-mono text-[10px] leading-relaxed text-faint">{RECEIPT.device}</p>
        <p className="mt-0.5 font-mono text-[10px] text-faint/70">{RECEIPT.stack}</p>
      </div>
    </aside>
  )
}
