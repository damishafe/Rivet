import { Link } from 'react-router-dom'

export function Hero() {
  return (
    <section className="skew-target relative min-h-screen w-full flex flex-col justify-center items-center overflow-hidden pt-20">
      <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-[#050505] z-10 pointer-events-none"></div>
      <div className="absolute inset-0 bg-gradient-to-r from-[#050505] via-transparent to-[#050505] z-10 pointer-events-none"></div>

      <div className="relative z-20 text-center max-w-5xl px-6 py-12">
        <div className="inline-flex items-center gap-3 border border-white/10 bg-white/5 px-4 py-1.5 rounded-full mb-8 backdrop-blur-sm">
          <span className="font-mono text-[10px] text-accent tracking-widest uppercase">
            Runs locally · AMD Radeon PRO W7900
          </span>
        </div>
        <h1 className="font-display font-bold text-5xl sm:text-6xl md:text-9xl tracking-tighter mb-6 leading-[0.9] text-white mix-blend-screen">
          <span className="scramble-text block">VERIFIED</span>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-400 to-gray-600 block">
            CAMPAIGNS
          </span>
        </h1>
        <p className="text-gray-400 text-base sm:text-lg md:text-xl max-w-2xl mx-auto leading-relaxed mb-10 font-light">
          A brief, a product shot and a logo become a three-scene ad. <br className="hidden md:block" />
          Generative where it's safe. Deterministic where it matters. Proof in every export.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center w-full sm:w-auto">
          <Link
            to="/studio"
            className="bg-accent text-black px-8 py-4 font-bold text-sm uppercase tracking-widest hover:bg-white transition-all w-full sm:w-auto btn-magnetic"
          >
            Open Studio
          </Link>
          <a
            href="#pipeline"
            className="px-8 py-4 border border-white/20 text-white font-bold text-sm uppercase tracking-widest hover:bg-white/10 transition-all w-full sm:w-auto btn-magnetic"
          >
            See the Pipeline
          </a>
        </div>
      </div>
    </section>
  )
}
