import { useEffect, useState } from 'react'
import { Icon } from '../components/icons/Icon'
import {
  Cancel01Icon,
  Download04Icon,
  PlayIcon,
  RefreshIcon,
} from '@hugeicons/core-free-icons'
import type { Scene } from './data'

function IconButton({
  icon,
  label,
  primary,
  disabled,
  onClick,
}: {
  icon: typeof PlayIcon
  label: string
  primary?: boolean
  disabled?: boolean
  onClick?: () => void
}) {
  return (
    <button
      disabled={disabled}
      onClick={onClick}
      aria-label={label}
      className={`group flex h-9 items-center gap-2 rounded-xl border px-3 text-[11px] font-medium transition-all duration-200 ${
        disabled
          ? 'cursor-not-allowed border-white/[0.04] bg-white/[0.02] text-faint/50'
          : primary
            ? 'border-accent/80 bg-accent text-white shadow-[0_8px_24px_rgba(255,59,0,0.22)] hover:-translate-y-0.5 hover:bg-accent-hover'
            : 'border-white/[0.07] bg-white/[0.045] text-muted hover:border-white/[0.12] hover:bg-white/[0.075] hover:text-foreground'
      }`}
    >
      <Icon icon={icon} size={15} />
      <span>{label}</span>
    </button>
  )
}

export function SceneCanvas({
  scene,
  running,
  onGenerate,
}: {
  scene: Scene
  running?: boolean
  onGenerate?: () => void
}) {
  const blocked = scene.checks.some((check) => check.status === 'fail')
  const [playing, setPlaying] = useState(false)
  const [exported, setExported] = useState(false)

  useEffect(() => {
    setPlaying(false)
    setExported(false)
  }, [scene.id, running])

  return (
    <div className="flex h-full min-w-0 flex-col bg-[#0d0d10]">
      <header className="flex h-[68px] shrink-0 items-center gap-4 border-b border-white/[0.06] px-4 sm:px-5">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h1 className="truncate font-display text-[15px] font-medium tracking-[-0.02em] text-foreground">
              {scene.label}
            </h1>
            <span
              className={`flex items-center gap-1.5 rounded-full border px-2 py-1 text-[9px] font-medium ${
                blocked
                  ? 'border-danger/20 bg-danger/10 text-danger'
                  : running
                    ? 'border-accent/20 bg-accent/10 text-accent'
                    : 'border-success/20 bg-success/10 text-success'
              }`}
            >
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  blocked ? 'bg-danger' : running ? 'animate-pulse bg-accent' : 'bg-success'
                }`}
              />
              {blocked ? 'Export blocked' : running ? 'Generating' : 'Verified'}
            </span>
          </div>
          <p className="mt-1 truncate text-[10px] text-faint">{scene.purpose}</p>
        </div>

        <div className="ml-auto hidden items-center gap-1.5 lg:flex">
          <span className="rounded-lg bg-white/[0.035] px-2 py-1.5 font-mono text-[9px] text-faint">
            9:16 · 5 SEC
          </span>
          <span className="rounded-lg bg-white/[0.035] px-2 py-1.5 font-mono text-[9px] text-faint">
            seed {scene.seed}
          </span>
        </div>
      </header>

      <div className="flex min-h-0 flex-1 flex-col gap-3 p-3 sm:p-4">
        <div
          className={`preview-stage relative min-h-0 flex-1 overflow-hidden rounded-[18px] border bg-[#111114] ${
            blocked ? 'border-danger/30' : 'border-white/[0.075]'
          }`}
        >
          <div
            aria-hidden="true"
            className="absolute -inset-8 scale-110 bg-cover bg-center opacity-60 blur-[34px]"
            style={{ backgroundImage: `url(${scene.still})` }}
          />
          <div
            aria-hidden="true"
            className="absolute inset-0 bg-[radial-gradient(circle_at_50%_42%,rgba(255,255,255,0.04),transparent_46%),linear-gradient(to_bottom,rgba(8,8,10,0.28),rgba(8,8,10,0.82))]"
          />
          <div aria-hidden="true" className="studio-grid absolute inset-0 opacity-20" />

          <div className="absolute inset-0 flex items-center justify-center p-4 sm:p-6">
            <div className="relative h-full max-h-[680px] overflow-hidden rounded-[14px] border border-white/10 bg-black shadow-[0_28px_70px_rgba(0,0,0,0.7)]">
              <img
                src={scene.still}
                alt={`${scene.label} scene`}
                className={`h-full w-auto object-contain ${playing ? 'scale-[1.008]' : ''}`}
              />
              <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 rounded-[inherit] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.04)]"
              />
              {running && <div className="scan-line" />}
            </div>
          </div>

          <div className="absolute left-3 top-3 flex items-center gap-2 rounded-lg border border-white/[0.08] bg-black/45 px-2.5 py-1.5 backdrop-blur-md">
            <span className={`h-1.5 w-1.5 rounded-full ${running ? 'animate-pulse bg-accent' : 'bg-success'}`} />
            <span className="font-mono text-[8px] uppercase tracking-[0.14em] text-white/65">
              {running ? 'Live render' : playing ? 'Preview playing' : 'Master preview'}
            </span>
          </div>

          <div className="absolute bottom-3 right-3 rounded-lg border border-white/[0.08] bg-black/45 px-2.5 py-1.5 font-mono text-[8px] text-white/55 backdrop-blur-md">
            00:00 / 00:05
          </div>
        </div>

        {blocked && (
          <div className="flex items-center gap-2 rounded-xl border border-danger/20 bg-danger/[0.07] px-3 py-2 text-[10px] text-danger">
            <span className="h-1.5 w-1.5 rounded-full bg-danger" />
            Product mismatch detected. Repair the scene before export.
          </div>
        )}

        <div className="rounded-[16px] border border-white/[0.065] bg-[#111114] px-3 py-2.5">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setPlaying((current) => !current)}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white text-black transition-transform hover:scale-105"
              aria-label={playing ? 'Pause preview' : 'Play preview'}
              disabled={running}
            >
              {playing ? (
                <span className="flex gap-1">
                  <span className="h-3 w-1 rounded-sm bg-black" />
                  <span className="h-3 w-1 rounded-sm bg-black" />
                </span>
              ) : (
                <Icon icon={PlayIcon} size={15} />
              )}
            </button>
            <div className="min-w-0 flex-1">
              <div className="relative h-1 overflow-hidden rounded-full bg-white/[0.08]">
                <div
                  className={`h-full rounded-full transition-[width] ${
                    running
                      ? 'w-[64%] animate-pulse bg-accent'
                      : playing
                        ? 'w-[78%] bg-white/70 duration-[4000ms]'
                        : 'w-[28%] bg-white/60 duration-300'
                  }`}
                />
              </div>
              <div className="mt-1.5 flex justify-between font-mono text-[8px] text-faint">
                <span>{running ? 'Rendering composition' : scene.headline}</span>
                <span>5.0 sec</span>
              </div>
            </div>

            <div className="hidden items-center gap-2 sm:flex">
              {running ? (
                <IconButton icon={Cancel01Icon} label="Cancel" />
              ) : (
                <>
                  <IconButton
                    icon={RefreshIcon}
                    label={blocked ? 'Repair scene' : 'Regenerate'}
                    onClick={onGenerate}
                  />
                  <IconButton
                    icon={Download04Icon}
                    label={blocked ? 'Export blocked' : exported ? 'Pack ready' : 'Export'}
                    primary={!blocked}
                    disabled={blocked}
                    onClick={() => setExported(true)}
                  />
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
