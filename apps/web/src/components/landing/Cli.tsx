export function Cli() {
  return (
    <section id="cli" className="skew-target py-24 bg-[#050505] border-t border-white/5 relative z-20">
      <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        <div className="order-2 lg:order-1">
          <span className="text-accent font-mono text-xs tracking-widest block mb-4">/// REPRODUCIBILITY</span>
          <h2 className="font-display font-bold text-4xl md:text-5xl mb-6 text-white scramble-text">Same Seed, Same Ad</h2>
          <p className="text-gray-400 text-lg mb-8 leading-relaxed">
            Every export embeds the exact command that recreates it — models pinned by revision, seeds saved, every
            input hashed. The GUI and CLI share one project state.
          </p>
          <div className="space-y-6">
            <div className="group flex gap-4 p-4 border border-transparent hover:border-white/10 rounded-lg transition-all cursor-pointer">
              <div className="font-mono text-gray-600 text-sm group-hover:text-accent">01</div>
              <div>
                <h4 className="font-bold text-white">make doctor</h4>
                <p className="text-sm text-gray-500">Verify the GPU, ROCm, PyTorch device and FFmpeg in one command.</p>
              </div>
            </div>
            <div className="group flex gap-4 p-4 border border-transparent hover:border-white/10 rounded-lg transition-all cursor-pointer">
              <div className="font-mono text-gray-600 text-sm group-hover:text-accent">02</div>
              <div>
                <h4 className="font-bold text-white">rivet run</h4>
                <p className="text-sm text-gray-500">Replay any campaign from its receipt — offline, cache-aware.</p>
              </div>
            </div>
          </div>
        </div>
        <div className="relative group order-1 lg:order-2">
          <div className="absolute -inset-1 bg-gradient-to-r from-accent to-purple-600 rounded-lg blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
          <div className="relative bg-[#0a0a0a] border border-white/10 rounded-lg p-6 font-mono text-xs sm:text-sm shadow-2xl overflow-x-auto min-h-[300px]">
            <div className="flex gap-2 mb-6 border-b border-white/5 pb-4">
              <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
            </div>
            <div className="text-gray-400 leading-relaxed">
              <div>
                <span className="text-purple-400">$</span> rivet create --name <span className="text-green-400">"Kora Arc Launch"</span>
              </div>
              <div>
                <span className="text-purple-400">$</span> rivet ingest kora --product <span className="text-green-400">product.png</span> --brief <span className="text-green-400">brief.wav</span>
              </div>
              <div>
                <span className="text-purple-400">$</span> rivet run kora --through audit
              </div>
              <div className="text-gray-600 pl-4">A01–A07 deterministic <span className="text-green-400">PASS</span></div>
              <div className="text-gray-600 pl-4">A08 semantic <span className="text-blue-400">86/100</span></div>
              <div>
                <span className="text-purple-400">$</span> rivet export kora --format campaign-pack
              </div>
              <div className="text-gray-600 pl-4">receipt <span className="text-blue-400">sha256:9c1f…e2ab</span></div>
            </div>
            <div className="mt-2 text-accent animate-pulse">_</div>
          </div>
        </div>
      </div>
    </section>
  )
}
