import { Link } from 'react-router-dom'

export function CampaignPack() {
  return (
    <section id="pack" className="skew-target py-32 px-6 bg-[#050505] relative z-20 border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <h2 className="font-display font-bold text-4xl text-white text-center mb-16 scramble-text">The Campaign Pack</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="border border-white/10 p-8 rounded-2xl hover:bg-white/5 transition-colors spotlight-card glass-panel">
            <div className="font-mono text-xs text-gray-500 mb-4 z-10 relative">/ CREATIVE</div>
            <div className="text-3xl font-bold text-white mb-6 z-10 relative">
              12–15s<span className="text-sm font-normal text-gray-500"> vertical ad</span>
            </div>
            <ul className="space-y-4 text-sm text-gray-300 mb-8 font-mono z-10 relative">
              <li className="flex gap-3"><span>✓</span> 1080×1920 MP4 + stills</li>
              <li className="flex gap-3"><span>✓</span> Narration, captions, SRT</li>
            </ul>
            <Link
              to="/studio"
              className="block text-center w-full py-3 border border-white/20 rounded font-bold uppercase text-xs tracking-wider text-white hover:bg-white hover:text-black transition-all z-10 relative"
            >
              Create One
            </Link>
          </div>

          <div className="border border-accent bg-[#0a0a0a] p-8 rounded-2xl relative transform md:-translate-y-4 shadow-[0_0_30px_rgba(255,59,0,0.1)] spotlight-card">
            <div className="absolute top-0 right-0 bg-accent text-black text-[10px] font-bold px-3 py-1 uppercase rounded-bl-lg z-10">
              The Point
            </div>
            <div className="font-mono text-xs text-accent mb-4 z-10 relative">/ PROOF</div>
            <div className="text-3xl font-bold text-white mb-6 z-10 relative">
              8 checks<span className="text-sm font-normal text-gray-500"> with evidence</span>
            </div>
            <ul className="space-y-4 text-sm text-gray-300 mb-8 font-mono z-10 relative">
              <li className="flex gap-3"><span className="text-accent">✓</span> Hashes, seeds, timings</li>
              <li className="flex gap-3"><span className="text-accent">✓</span> Repair history, VRAM peaks</li>
            </ul>
            <Link
              to="/studio"
              className="block text-center w-full py-3 bg-accent text-black rounded font-bold uppercase text-xs tracking-wider hover:bg-white transition-all z-10 relative"
            >
              See a Receipt
            </Link>
          </div>

          <div className="border border-white/10 p-8 rounded-2xl hover:bg-white/5 transition-colors spotlight-card glass-panel">
            <div className="font-mono text-xs text-gray-500 mb-4 z-10 relative">/ REPRO</div>
            <div className="text-3xl font-bold text-white mb-6 z-10 relative">
              1 command<span className="text-sm font-normal text-gray-500"> to replay</span>
            </div>
            <ul className="space-y-4 text-sm text-gray-300 mb-8 font-mono z-10 relative">
              <li className="flex gap-3"><span>✓</span> Models pinned by revision</li>
              <li className="flex gap-3"><span>✓</span> Runs fully offline</li>
            </ul>
            <a
              href="https://github.com/damishafe/Rivet"
              className="block text-center w-full py-3 border border-white/20 rounded font-bold uppercase text-xs tracking-wider text-white hover:bg-white hover:text-black transition-all z-10 relative"
            >
              View Source
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
