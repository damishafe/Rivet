import { useState } from 'react'
import { Icon } from '../components/icons/Icon'
import { Cancel01Icon, CheckmarkCircle02Icon } from '@hugeicons/core-free-icons'
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

function CheckRow({ check }: { check: Check }) {
  const failed = check.status === 'fail'
  const advisory = check.status === 'advisory'

  return (
    <div className="group flex items-center gap-3 border-b border-white/[0.045] py-2.5 last:border-0">
      <span
        className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full ${
          failed ? 'bg-danger/10 text-danger' : advisory ? 'bg-white/[0.05] text-faint' : 'bg-success/10 text-success'
        }`}
      >
        <Icon icon={failed ? Cancel01Icon : CheckmarkCircle02Icon} size={12} />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-[11px] font-medium text-muted">{check.metric}</span>
        <span className="mt-0.5 block truncate font-mono text-[8px] text-faint">
          {check.id} · {check.threshold}
        </span>
      </span>
      <span className={`font-mono text-[10px] ${failed ? 'text-danger' : 'text-muted'}`}>
        {check.observed}
      </span>
    </div>
  )
}

function ReceiptRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 py-1.5">
      <span className="text-[9px] text-faint">{label}</span>
      <span className="max-w-[175px] truncate font-mono text-[8px] text-muted">{value}</span>
    </div>
  )
}

export function AuditPanel({ scene }: { scene: Scene }) {
  const [receiptOpen, setReceiptOpen] = useState(false)
  const checks = [...scene.checks, ADVISORY]
  const failed = checks.filter((check) => check.status === 'fail')
  const verified = failed.length === 0
  const score = verified ? 100 : Math.round(((checks.length - failed.length) / checks.length) * 100)

  return (
    <div className="flex h-full flex-col">
      <header className="flex h-[68px] shrink-0 items-center justify-between border-b border-white/[0.06] px-4">
        <div>
          <h2 className="font-display text-[13px] font-medium tracking-[-0.01em] text-foreground">
            Quality control
          </h2>
          <p className="mt-1 text-[9px] text-faint">Deterministic scene audit</p>
        </div>
        <span className="rounded-lg border border-white/[0.07] bg-white/[0.035] px-2 py-1 font-mono text-[8px] uppercase tracking-[0.12em] text-faint">
          A01–A10
        </span>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        <section
          className={`relative overflow-hidden rounded-[16px] border p-4 ${
            verified
              ? 'border-success/15 bg-[linear-gradient(145deg,rgba(52,211,153,0.10),rgba(255,255,255,0.025))]'
              : 'border-danger/20 bg-[linear-gradient(145deg,rgba(248,113,113,0.11),rgba(255,255,255,0.025))]'
          }`}
        >
          <div
            aria-hidden="true"
            className={`absolute -right-10 -top-10 h-28 w-28 rounded-full blur-3xl ${
              verified ? 'bg-success/15' : 'bg-danger/15'
            }`}
          />
          <div className="relative flex items-center justify-between">
            <div>
              <p className={`text-[10px] font-medium ${verified ? 'text-success' : 'text-danger'}`}>
                {verified ? 'Ready for export' : 'Action required'}
              </p>
              <p className="mt-2 font-display text-[20px] font-medium tracking-[-0.035em] text-foreground">
                {verified ? 'Scene verified' : 'Export blocked'}
              </p>
              <p className="mt-1.5 text-[9px] leading-relaxed text-faint">
                {verified
                  ? 'Every production guardrail passed.'
                  : `${failed.length} critical check must be repaired.`}
              </p>
            </div>
            <div
              className="grid h-16 w-16 place-items-center rounded-full"
              style={{
                background: `radial-gradient(circle at center, #0e0e11 59%, transparent 60%), conic-gradient(${verified ? '#34d399' : '#f87171'} ${score}%, rgba(255,255,255,0.07) 0)`,
              }}
            >
              <span className="font-display text-[14px] font-medium text-foreground">{score}%</span>
            </div>
          </div>
        </section>

        <section className="mt-5">
          <div className="mb-1 flex items-center justify-between">
            <h3 className="text-[10px] font-medium uppercase tracking-[0.14em] text-faint">
              Production checks
            </h3>
            <span className="font-mono text-[8px] text-faint">
              {checks.length - failed.length}/{checks.length} passed
            </span>
          </div>
          <div>
            {checks.map((check) => (
              <CheckRow key={check.id} check={check} />
            ))}
          </div>
        </section>

        <section className="mt-5 rounded-[14px] border border-white/[0.06] bg-white/[0.025]">
          <button
            onClick={() => setReceiptOpen((current) => !current)}
            className="flex w-full items-center justify-between px-3 py-3 text-left"
          >
            <span>
              <span className="block text-[10px] font-medium text-muted">Campaign receipt</span>
              <span className="mt-1 block font-mono text-[8px] text-faint">
                Signed provenance record
              </span>
            </span>
            <span className="rounded-md bg-white/[0.04] px-2 py-1 font-mono text-[8px] text-muted">
              {RECEIPT.hash.slice(0, 8)}…
            </span>
          </button>
          {receiptOpen && (
            <div className="border-t border-white/[0.055] px-3 py-2">
              <ReceiptRow label="Receipt" value={RECEIPT.hash} />
              <ReceiptRow label="Content digest" value={RECEIPT.contentDigest} />
              <ReceiptRow label="Seed" value={String(scene.seed)} />
              <ReceiptRow label="Product" value={RECEIPT.productSha} />
              <ReceiptRow label="Logo" value={RECEIPT.logoSha} />
              <ReceiptRow label="Peak VRAM" value={`${RECEIPT.peakVramMb} MB`} />
            </div>
          )}
        </section>
      </div>

      <footer className="shrink-0 border-t border-white/[0.06] px-4 py-3">
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-2 text-[9px] text-faint">
            <span className="h-1.5 w-1.5 rounded-full bg-success shadow-[0_0_8px_rgba(52,211,153,0.55)]" />
            Receipt service online
          </span>
          <span className="font-mono text-[8px] text-faint">67.8s cold</span>
        </div>
      </footer>
    </div>
  )
}
