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
import type { Mode } from '../pages/Studio'

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
  mode: Mode
  modes: { id: Mode; label: string }[]
  onModeSelect: (mode: Mode) => void
}

export function Sidebar({ scenes, activeId, onSelect, mode, modes, onModeSelect }: Props) {
  return (
    <aside className="hidden w-[238px] shrink-0 flex-col bg-[#09090b] md:flex">
      <div className="flex h-[68px] items-center gap-2.5 border-b border-white/[0.06] px-5">
        <img
          src="/logo.png"
          alt=""
          className="h-8 w-8 rounded-xl border border-white/10 object-cover shadow-lg shadow-black/30"
        />
        <span className="font-display text-[15px] font-semibold tracking-[-0.02em] text-foreground">
          Rivet
        </span>
        <span className="rounded-md border border-white/[0.08] bg-white/[0.04] px-1.5 py-0.5 font-mono text-[8px] uppercase tracking-[0.12em] text-faint">
          Studio
        </span>
        <Link
          to="/"
          className="ml-auto cursor-pointer text-faint transition-colors hover:text-foreground"
          aria-label="Back"
        >
          <Icon icon={ArrowLeft01Icon} size={16} />
        </Link>
      </div>

      <div className="px-3 pt-5">
        <p className="px-2 pb-2 text-[10px] font-medium uppercase tracking-[0.16em] text-faint/70">
          Workflow
        </p>
      <nav className="space-y-1">
        {STEPS.map((step) => (
          <div
            key={step.label}
            className={`group flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] transition-all ${
              step.current
                ? 'bg-white/[0.07] text-foreground shadow-[inset_0_0_0_1px_rgba(255,255,255,0.04)]'
                : 'text-faint hover:bg-white/[0.035] hover:text-muted'
            }`}
          >
            <Icon
              icon={step.icon}
              size={16}
              className={step.current ? 'text-accent' : 'text-faint transition-colors group-hover:text-muted'}
            />
            {step.label}
            {step.current && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-accent shadow-[0_0_10px_rgba(255,59,0,0.65)]" />}
          </div>
        ))}
      </nav>
      </div>

      <div className="mt-6 flex items-center justify-between px-5">
        <p className="text-[10px] font-medium uppercase tracking-[0.16em] text-faint/70">Scenes</p>
        <span className="font-mono text-[9px] text-faint">{scenes.length} / 3</span>
      </div>
      <div className="mt-2 space-y-1 px-3">
        {scenes.map((scene) => {
          const active = scene.id === activeId
          const failing = scene.checks.some((c) => c.status === 'fail')
          return (
            <button
              key={scene.id}
              onClick={() => onSelect(scene.id)}
              className={`group flex w-full cursor-pointer items-center gap-3 rounded-xl p-2 text-left transition-all ${
                active
                  ? 'bg-white/[0.065] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.04)]'
                  : 'hover:bg-white/[0.03]'
              }`}
            >
              <div className="relative h-12 w-8 shrink-0 overflow-hidden rounded-md bg-elevated">
                <img src={scene.still} alt="" className="h-full w-full object-cover" />
                {active && <span className="absolute inset-x-0 bottom-0 h-0.5 bg-accent" />}
              </div>
              <span className="min-w-0 flex-1">
                <span
                  className={`block truncate text-[12px] font-medium ${
                    active ? 'text-foreground' : 'text-muted'
                  }`}
                >
                  {scene.label}
                </span>
                <span className="mt-0.5 block truncate text-[9px] text-faint">
                  {scene.purpose}
                </span>
              </span>
              <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${failing ? 'bg-danger' : 'bg-success'}`} />
            </button>
          )
        })}
      </div>

      <div className="mt-auto border-t border-white/[0.06] p-3">
        <div className="rounded-xl bg-white/[0.035] p-2">
          <p className="px-1 pb-1.5 text-[9px] uppercase tracking-[0.14em] text-faint/70">
            Demo state
          </p>
          <div className="grid grid-cols-3 gap-1">
            {modes.map((option) => (
              <button
                key={option.id}
                onClick={() => onModeSelect(option.id)}
                className={`rounded-lg px-1 py-1.5 text-[9px] font-medium transition-all ${
                  mode === option.id
                    ? 'bg-white/[0.09] text-foreground shadow-sm'
                    : 'text-faint hover:bg-white/[0.04] hover:text-muted'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
        <div className="mt-3 flex items-center gap-2 px-1">
          <span className="h-2 w-2 rounded-full bg-success shadow-[0_0_10px_rgba(52,211,153,0.5)]" />
          <div className="min-w-0">
            <p className="truncate text-[9px] text-muted">Radeon PRO W7900</p>
            <p className="mt-0.5 truncate font-mono text-[8px] text-faint">
              {RECEIPT.stack} · ready
            </p>
          </div>
        </div>
      </div>
    </aside>
  )
}
