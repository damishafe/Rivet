const STEPS = [
  {
    title: '01. Ingest & Lock',
    body: 'A brief, a product shot and a logo become confirmed Brand DNA. Protected assets are hashed and cut out at the source.',
  },
  {
    title: '02. Generate',
    body: 'Backgrounds and hero motion render locally on the W7900. Protected layers are composited after — the model never touches them.',
  },
  {
    title: '03. Verify & Repair',
    body: 'Eight checks run with evidence. A failure reruns only its owner stage, and every export ships with a receipt.',
  },
]

export function Pipeline() {
  return (
    <section id="pipeline" className="py-24 bg-[#050505] relative z-20 border-t border-white/5">
      <div className="max-w-[1400px] mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 relative">
          <div className="order-2 lg:order-1 relative">
            <div className="sticky top-24 w-full aspect-square max-h-[50vh] lg:max-h-[60vh] bg-[#080808] border border-white/10 rounded-2xl overflow-hidden flex items-center justify-center p-10 group shadow-2xl">
              <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:20px_20px]"></div>

              <div className="relative w-32 h-32 md:w-40 md:h-40 border border-accent rounded-full flex items-center justify-center z-10 shadow-[0_0_50px_rgba(255,59,0,0.3)] bg-black/50 backdrop-blur-sm">
                <div className="w-24 h-24 md:w-32 md:h-32 bg-accent/10 rounded-full animate-pulse"></div>
                <div className="absolute text-white font-mono text-[10px] md:text-xs tracking-widest">VERIFYING</div>
              </div>

              <div className="absolute w-[70%] h-[70%] border border-white/5 rounded-full animate-spin-slow">
                <div className="w-4 h-4 bg-white rounded-full absolute -top-2 left-1/2 -translate-x-1/2 shadow-[0_0_15px_white]"></div>
              </div>
              <div className="absolute w-[90%] h-[90%] border border-white/5 rounded-full animate-reverse-spin">
                <div className="w-3 h-3 bg-accent rounded-full absolute -top-1.5 left-1/2 -translate-x-1/2"></div>
              </div>
            </div>
          </div>

          <div className="order-1 lg:order-2 lg:py-20 pb-0">
            <span className="text-accent font-mono text-xs tracking-widest block mb-10">/// THE PIPELINE</span>

            {STEPS.map((step, i) => (
              <div
                key={step.title}
                className={`step-item opacity-30 transition-opacity duration-500 ${i < STEPS.length - 1 ? 'mb-24 md:mb-48' : ''}`}
              >
                <h3 className="text-3xl md:text-4xl font-display font-bold mb-4 text-white">{step.title}</h3>
                <p className="text-lg md:text-xl text-white leading-relaxed font-light">{step.body}</p>
              </div>
            ))}

            <div className="h-20 lg:h-40"></div>
          </div>
        </div>
      </div>
    </section>
  )
}
