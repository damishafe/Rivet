export type CheckStatus = 'pass' | 'fail' | 'advisory'

export type Check = {
  id: string
  metric: string
  threshold: string
  observed: string
  status: CheckStatus
  owner: string
}

export type Scene = {
  id: 'hook' | 'proof' | 'cta'
  label: string
  purpose: string
  still: string
  seed: number
  headline: string
  support: string
  cta: string
  narration: string
  backgroundPrompt: string
  checks: Check[]
}

export type Stage = {
  name: string
  seconds: number
  vramMb: number | null
  state: 'done' | 'running' | 'queued'
  cache: 'miss' | 'hit'
}

const pass = (
  id: string,
  metric: string,
  threshold: string,
  observed: string,
  owner: string,
): Check => ({ id, metric, threshold, observed, status: 'pass', owner })

const verifiedChecks: Check[] = [
  pass('A01', 'protected asset lineage', 'exact sha256 match', 'match', 'compose'),
  pass('A02', 'logo fidelity mean pixel diff', '<= 40', '9.3', 'layout'),
  pass('A03', 'rendered copy equals approved copy', 'exact string match', 'match', 'copy/layout'),
  pass('A04', 'saturated colour hue vs palette', '<= 40 degrees', '1.9', 'background/layout'),
  pass('A05', 'safe-area geometry and text overflow', '0 violations', '0', 'layout'),
  pass('A06', 'planned product share of frame', '>= 0.05', '0.151', 'layout/mask'),
  pass('A07', 'forbidden claims and required phrases', '0 forbidden + all required', 'clean', 'copy'),
  pass('A09', 'product fidelity mean pixel diff', '<= 40', '0.0', 'compose'),
  pass('A10', 'text contrast ratio', '>= 4.0', '7.28', 'layout'),
]

export const RECEIPT = {
  hash: 'c6914739cccdd9cb',
  projectId: '66ea75d2bc9f44dfa9b9ea93caf9aefe',
  productSha: '4f2c9a71e8b3d5064c1a7f93be2085d7',
  logoSha: 'b81e5d0a37c94f26ae5731c08df9b642',
  device: 'AMD Radeon Graphics · gfx1100 · 49136 MB',
  stack: 'ROCm 7.2.53211 · torch 2.9.1',
  coldSeconds: 67.8,
  peakVramMb: 9168,
  contentDigest: '347606b58a93ba16',
}

export const SCENES: Scene[] = [
  {
    id: 'hook',
    label: 'Hook',
    purpose: 'Grab attention in the first second',
    still: '/scene-hook.jpg',
    seed: 1766111147,
    headline: 'Meet Kora Arc',
    support: 'Simple. Modern. Powerful.',
    cta: 'Discover it now',
    narration: 'Your ideas deserve a clear sound, no matter where you are.',
    backgroundPrompt: 'soft neutral studio wall with directional light',
    checks: verifiedChecks,
  },
  {
    id: 'proof',
    label: 'Proof',
    purpose: 'Give a concrete reason to believe',
    still: '/scene-cta.jpg',
    seed: 1766111148,
    headline: 'Clean Sound. Clean Design.',
    support: 'Engineered for clarity and calm.',
    cta: 'Try it today',
    narration: 'Lightweight, durable, and engineered for your daily hustle.',
    backgroundPrompt: 'bare concrete desk surface with soft directional light',
    checks: verifiedChecks,
  },
  {
    id: 'cta',
    label: 'Call to action',
    purpose: 'Close with the action',
    still: '/scene-cta.jpg',
    seed: 1766111149,
    headline: 'Start Listening',
    support: 'Available now in stores.',
    cta: 'Shop now',
    narration: 'Unlock your creativity. One click. One charge. One sound.',
    backgroundPrompt: 'warm plaster wall, low evening light',
    checks: verifiedChecks,
  },
]

export const BLOCKED_SCENE: Scene = {
  ...SCENES[0],
  still: '/scene-blocked.jpg',
  checks: verifiedChecks.map((check) =>
    check.id === 'A01'
      ? { ...check, observed: 'mismatch', status: 'fail' as CheckStatus }
      : check,
  ),
}

export const STAGES: Stage[] = [
  { name: 'segment', seconds: 0.08, vramMb: 8595, state: 'done', cache: 'miss' },
  { name: 'background.hook', seconds: 11.59, vramMb: 9168, state: 'done', cache: 'miss' },
  { name: 'composite.hook', seconds: 0.41, vramMb: 6800, state: 'done', cache: 'miss' },
  { name: 'background.proof', seconds: 3.29, vramMb: 9164, state: 'done', cache: 'miss' },
  { name: 'composite.proof', seconds: 0.59, vramMb: 6800, state: 'done', cache: 'miss' },
  { name: 'background.cta', seconds: 3.36, vramMb: 9164, state: 'done', cache: 'miss' },
  { name: 'composite.cta', seconds: 0.59, vramMb: 6800, state: 'done', cache: 'miss' },
  { name: 'motion.hook', seconds: 0.89, vramMb: 6800, state: 'done', cache: 'miss' },
  { name: 'narration.hook', seconds: 10.44, vramMb: 6800, state: 'running', cache: 'miss' },
  { name: 'motion.proof', seconds: 0, vramMb: null, state: 'queued', cache: 'miss' },
  { name: 'narration.proof', seconds: 0, vramMb: null, state: 'queued', cache: 'miss' },
  { name: 'motion.cta', seconds: 0, vramMb: null, state: 'queued', cache: 'miss' },
  { name: 'narration.cta', seconds: 0, vramMb: null, state: 'queued', cache: 'miss' },
]
