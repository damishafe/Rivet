import { useState } from 'react'
import { Icon } from '../components/icons/Icon'
import {
  Cancel01Icon,
  CheckmarkCircle02Icon,
} from '@hugeicons/core-free-icons'
import type { Check, Scene } from './data'
import { RECEIPT } from './data'

const ADVISORY: Check = {
  id: 'A08',
  metric: 'semantic fit',
  threshold: '>= 80',
  observed: '82',
  status: 'advisory',
  owner: 'plan',
}

function Card({ children }: { children: React.ReactNode }) {
  return <div className="rounded-xl border border-border bg-elevated/40 p-4">{children}</div>
}

function Verdict({ scene }: { scene: Scene }) {
  const failed = scene.checks.filter((c) => c.status === 'fail')
  const verified = failed.length === 0

  return (
    <Card>
      <div className="flex items-center gap-3">
        <Icon
          icon={verified ? CheckmarkCircle02Icon : Cancel01Icon}
          size={22}
          className={verified ? 'text-success' : 'text-danger'}
        />
        <div>
          <p className="font-display text-[17px] font-medium leading-none tracking-tight text-foreground">
            {verified ? 'Verified' : 'Export blocked'}
          </p>
          <p className="mt-1.5 text-[12px] text-muted">
            {verified
              ? `${scene.checks.length} of ${scene.checks.length} checks passed`
              : `${failed.length} check failed · no pack written`}
          </p>
        </div>
      </div>
    </Card>
  )
}

function CheckRow({ check }: { check: Check }) {
  const failed = check.status === 'fail'
  const advisory = check.status === 'advisory'
  return (
    <div className="flex items-center gap-3 py-2">
      <span
        className={`h-1.5 w-1.5 shrink-0 rounded-full ${
          failed ? 'bg-danger' : advisory ? 'bg-faint' : 'bg-success'
        }`}
      />
      <span className="w-8 shrink-0 font-mono text-[12px] text-muted">{check.id}</span>
      <span className="min-w-0 flex-1 truncate text-[13px] text-foreground">{check.metric}</span>
      <span
        className={`shrink-0 font-mono text-[12px] ${failed ? 'text-danger' : 'text-faint'}`}
      >
        {check.observed}
      </span>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 py-1.5">
      <span className="shrink-0 text-[12px] text-faint">{label}</span>
      <span className="truncate font-mono text-[12px] text-muted">{value}</span>
    </div>
  )
}

export function AuditPanel({ scene }: { scene: Scene }) {
  const [open, setOpen] = useState(false)
  const checks = [...scene.checks, ADVISORY]

  return (
    <div className="flex h-full flex-col gap-3 overflow-y-auto p-4">
      <Verdict scene={scene} />

      <Card>
        <p className="mb-1 font-display text-[13px] font-medium tracking-tight text-foreground">
          Checks
        </p>
        <div className="divide-y divide-border/50">
          {checks.map((check) => (
            <CheckRow key={check.id} check={check} />
          ))}
        </div>
      </Card>

      <Card>
        <button
          onClick={() => setOpen(!open)}
          className="flex w-full cursor-pointer items-center justify-between"
        >
          <span className="font-display text-[13px] font-medium tracking-tight text-foreground">
            Campaign Receipt
          </span>
          <span className="font-mono text-[12px] text-muted">{RECEIPT.hash.slice(0, 8)}…</span>
        </button>
        {open && (
          <div className="mt-3 border-t border-border/60 pt-2">
            <Row label="receipt" value={RECEIPT.hash} />
            <Row label="content digest" value={RECEIPT.contentDigest} />
            <Row label="seed" value={String(scene.seed)} />
            <Row label="product" value={`${RECEIPT.productSha.slice(0, 12)}…`} />
            <Row label="logo" value={`${RECEIPT.logoSha.slice(0, 12)}…`} />
            <Row label="peak VRAM" value={`${RECEIPT.peakVramMb} MB`} />
          </div>
        )}
        {!open && (
          <p className="mt-2 text-[12px] leading-relaxed text-faint">
            Input hashes, seeds, timings and every check — signed over the whole record.
          </p>
        )}
      </Card>
    </div>
  )
}
