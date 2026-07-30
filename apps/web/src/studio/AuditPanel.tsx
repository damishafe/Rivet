import { Icon } from '../components/icons/Icon'
import { Cancel01Icon, CheckmarkCircle02Icon, InformationCircleIcon } from '@hugeicons/core-free-icons'
import type { Check, Scene } from './data'
import { RECEIPT } from './data'

const ADVISORY: Check = {
  id: 'A08',
  metric: 'semantic alignment score',
  threshold: '>= 80',
  observed: '82 — calm, premium audio brand',
  status: 'advisory',
  owner: 'plan/background',
}

function StatusMark({ status }: { status: Check['status'] }) {
  if (status === 'fail') {
    return <Icon icon={Cancel01Icon} size={15} className="shrink-0 text-danger" />
  }
  if (status === 'advisory') {
    return <Icon icon={InformationCircleIcon} size={15} className="shrink-0 text-muted" />
  }
  return <Icon icon={CheckmarkCircle02Icon} size={15} className="shrink-0 text-success" />
}

function CheckRow({ check }: { check: Check }) {
  const failed = check.status === 'fail'
  return (
    <div
      className={`flex items-start gap-2.5 border-b border-border/60 px-4 py-2.5 last:border-0 ${
        failed ? 'bg-danger/5' : ''
      }`}
    >
      <span className="mt-0.5">
        <StatusMark status={check.status} />
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2">
          <span className="font-mono text-[11px] font-medium text-foreground">{check.id}</span>
          <span className="truncate text-[12px] text-muted">{check.metric}</span>
        </div>
        <div className="mt-0.5 flex items-baseline gap-2 font-mono text-[10px]">
          <span className={failed ? 'text-danger' : 'text-faint'}>{check.observed}</span>
          <span className="text-faint/60">/ {check.threshold}</span>
        </div>
      </div>
      {check.status === 'advisory' && (
        <span className="mt-0.5 shrink-0 rounded-full border border-border px-1.5 py-px font-mono text-[9px] text-faint">
          advisory
        </span>
      )}
    </div>
  )
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3 py-1">
      <span className="shrink-0 text-[11px] text-faint">{label}</span>
      <span className="truncate font-mono text-[10px] text-muted">{value}</span>
    </div>
  )
}

export function AuditPanel({ scene }: { scene: Scene }) {
  const checks = [...scene.checks, ADVISORY]
  const blocking = scene.checks.filter((c) => c.status === 'fail')
  const passed = scene.checks.filter((c) => c.status === 'pass').length
  const verified = blocking.length === 0

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border px-4 py-3.5">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-[13px] font-medium tracking-tight text-foreground">
            Audit
          </h2>
          <span
            className={`rounded-full border px-2 py-0.5 font-mono text-[10px] ${
              verified
                ? 'border-success/30 bg-success/10 text-success'
                : 'border-danger/30 bg-danger/10 text-danger'
            }`}
          >
            {verified ? `${passed}/${scene.checks.length} verified` : 'export blocked'}
          </span>
        </div>
        <p className="mt-1.5 text-[11px] leading-relaxed text-faint">
          {verified
            ? 'Every deterministic check passed. The export pack is written.'
            : 'A deterministic check failed. No pack is written and the project moves to needs_repair.'}
        </p>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {checks.map((check) => (
          <CheckRow key={check.id} check={check} />
        ))}
      </div>

      <div className="border-t border-border px-4 py-3">
        <h3 className="font-display text-[11px] font-medium tracking-tight text-foreground">
          Campaign Receipt
        </h3>
        <div className="mt-1.5">
          <Field label="receipt" value={RECEIPT.hash} />
          <Field label="content digest" value={RECEIPT.contentDigest} />
          <Field label="seed" value={String(scene.seed)} />
          <Field label="product sha256" value={`${RECEIPT.productSha.slice(0, 16)}…`} />
          <Field label="logo sha256" value={`${RECEIPT.logoSha.slice(0, 16)}…`} />
          <Field label="peak VRAM" value={`${RECEIPT.peakVramMb} MB`} />
          <Field label="cold total" value={`${RECEIPT.coldSeconds}s`} />
        </div>
      </div>
    </div>
  )
}
