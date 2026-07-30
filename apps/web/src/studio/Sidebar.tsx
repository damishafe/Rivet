import { Link } from 'react-router-dom'
import { Icon } from '../components/icons/Icon'
import {
  ArrowLeft01Icon,
  ImageAdd02Icon,
  PaintBoardIcon,
  ShieldKeyIcon,
  SparklesIcon,
} from '@hugeicons/core-free-icons'
import type { Scene } from './data'
import { RECEIPT } from './data'

const STEPS = [
  { label: 'Project', icon: ImageAdd02Icon },
  { label: 'Brand DNA', icon: PaintBoardIcon },
  { label: 'Storyboard', icon: SparklesIcon },
  { label: 'Review', icon: ShieldKeyIcon, current: true },
]

type Props = {
  scenes: Scene[]
  activeId: string
  onSelect: (id: Scene['id']) => void
}

export function Sidebar({ scenes, activeId, onSelect }: Props) {
  return (
    <aside className="flex w-[224px] shrink-0 flex-col p-4">
      <div className="flex items-center gap-2.5 px-2 pb-6">
        <img src="/logo.png" alt="" className="h-7 w-7 rounded-full object-cover" />
        <span className="font-display text-[15px] font-semibold tracking-tight text-foreground">
          Rivet
        </span>
        <Link
          to="/"
          className="ml-auto cursor-pointer text-faint transition-colors hover:text-foreground"
          aria-label="Back"
        >
          <Icon icon={ArrowLeft01Icon} size={16} />
        </Link>
      </div>

      <nav className="space-y-0.5">
        {STEPS.map((step) => (
          <div
            key={step.label}
            className={`flex cursor-pointer items-center gap-3 rounded-lg px-3 py-2.5 text-[14px] transition-colors ${
              step.current
                ? 'bg-elevated text-foreground'
                : 'text-muted hover:bg-elevated/40 hover:text-foreground'
            }`}
          >
            <Icon icon={step.icon} size={17} className={step.current ? '' : 'text-faint'} />
            {step.label}
          </div>
        ))}
      </nav>

      <p className="px-3 pb-2 pt-7 text-[12px] text-faint">Scenes</p>
      <div className="space-y-1">
        {scenes.map((scene) => {
          const active = scene.id === activeId
          const failing = scene.checks.some((c) => c.status === 'fail')
          return (
            <button
              key={scene.id}
              onClick={() => onSelect(scene.id)}
              className={`flex w-full cursor-pointer items-center gap-3 rounded-lg p-2 text-left transition-colors ${
                active ? 'bg-elevated' : 'hover:bg-elevated/40'
              }`}
            >
              <img
                src={scene.still}
                alt=""
                className="h-9 w-[22px] shrink-0 rounded border border-border object-cover"
              />
              <span
                className={`flex-1 truncate text-[13px] ${
                  active ? 'text-foreground' : 'text-muted'
                }`}
              >
                {scene.label}
              </span>
              <span
                className={`h-1.5 w-1.5 shrink-0 rounded-full ${failing ? 'bg-danger' : 'bg-success'}`}
              />
            </button>
          )
        })}
      </div>

      <div className="mt-auto px-3">
        <p className="text-[11px] leading-relaxed text-faint">{RECEIPT.device}</p>
        <p className="mt-1 text-[11px] text-faint/60">{RECEIPT.stack}</p>
      </div>
    </aside>
  )
}
