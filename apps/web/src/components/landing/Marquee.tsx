const STACK = ['WHISPER', 'QWEN3-VL', 'SAM 2.1', 'FLUX.1', 'LTX-VIDEO', 'KOKORO', 'ROCm', 'FFMPEG']

export function Marquee() {
  return (
    <div className="border-y border-white/5 bg-[#080808] py-8 relative z-20 overflow-hidden marquee-mask w-full">
      <div className="flex whitespace-nowrap animate-marquee w-[max-content]">
        {[0, 1, 2].map((copy) => (
          <div key={copy} className="flex gap-12 md:gap-20 px-6 md:px-10 items-center">
            {STACK.map((name) => (
              <span
                key={name}
                className="font-display font-bold text-xl md:text-2xl text-white/30 hover:text-white transition-colors"
              >
                {name}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
