import { Layers01Icon, LockIcon, Activity01Icon } from '@hugeicons/core-free-icons'
import { Icon } from '@/components/icons/Icon'

export function Bento() {
  return (
    <section id="guarantees" className="skew-target py-24 md:py-32 px-6 relative z-20">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-16 border-b border-white/10 pb-8 gap-6 md:gap-0">
          <div>
            <span className="text-accent font-mono text-xs tracking-widest block mb-2">/// THE GUARANTEES</span>
            <h2 className="font-display font-bold text-white text-4xl md:text-5xl scramble-text">Proof Engine</h2>
          </div>
          <div className="text-left md:text-right w-full md:w-auto">
            <div className="flex items-center md:justify-end gap-2 mb-1">
              <span className="w-2 h-2 bg-success rounded-full animate-blink"></span>
              <span className="font-mono text-xs text-white">GPU: W7900 · 48GB</span>
            </div>
            <p className="text-gray-500 font-mono text-xs uppercase tracking-widest">Peak VRAM budget: 44GB</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 md:grid-rows-3 gap-6 h-auto md:h-[900px]">
          <div className="md:col-span-2 md:row-span-2 min-h-[300px] glass-panel spotlight-card rounded-xl overflow-hidden relative group">
            <div className="scan-line"></div>
            <img
              src="/black-speaker.png"
              className="absolute inset-0 w-full h-full object-cover opacity-50 mix-blend-luminosity group-hover:scale-105 transition-transform duration-700"
              alt="Exploded speaker layers"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
            <div className="absolute top-6 right-6 border border-white/20 bg-black/50 px-3 py-1 rounded text-[10px] font-mono text-accent">
              COMPOSITING_SCENE_02
            </div>
            <div className="absolute bottom-0 left-0 p-8 z-10 w-full">
              <div className="w-10 h-10 bg-accent flex items-center justify-center mb-4 text-black font-bold">
                <Icon icon={Layers01Icon} size={24} strokeWidth={2} />
              </div>
              <h3 className="font-display font-bold text-2xl text-white mb-2">Protected Layers</h3>
              <p className="text-gray-300 text-sm max-w-sm">
                Product, logo and typography are composited from source assets after generation — never redrawn by the
                model.
              </p>
            </div>
          </div>

          <div className="md:col-span-1 md:row-span-1 glass-panel spotlight-card rounded-xl p-6 flex flex-col justify-between h-40 md:h-auto">
            <div className="flex justify-between items-start">
              <span className="font-mono text-[10px] text-gray-500 uppercase">Audit</span>
              <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse"></div>
            </div>
            <div className="text-center py-2">
              <div className="text-4xl font-display font-bold text-white">
                <span className="counter" data-target="8">8</span>/8
              </div>
              <div className="text-[10px] text-gray-500 mt-1">Checks to PASS</div>
            </div>
          </div>

          <div className="md:col-span-1 md:row-span-1 glass-panel spotlight-card rounded-xl p-6 flex flex-col justify-between overflow-hidden h-40 md:h-auto">
            <div className="flex items-center gap-2 text-white mb-2">
              <Icon icon={LockIcon} size={14} strokeWidth={2} />
              <span className="font-display font-bold text-sm">Lineage</span>
            </div>
            <div className="relative h-12 overflow-hidden font-mono text-[9px] text-gray-600 leading-relaxed">
              <div className="animate-[marquee_5s_linear_infinite_reverse] flex flex-col">
                <span>0x7f8d9a2b3c4d5e6f</span>
                <span>0x1a2b3c4d5e6f7a8b</span>
                <span>0x9c8d7e6f5a4b3c2d</span>
                <span>0x1f2e3d4c5b6a7988</span>
              </div>
            </div>
            <div className="text-[10px] text-accent mt-2 flex items-center gap-1">
              <span className="w-1 h-1 bg-accent rounded-full"></span> SHA-256 IN EVERY EXPORT
            </div>
          </div>

          <div className="md:col-span-1 md:row-span-1 glass-panel spotlight-card rounded-xl p-6 flex flex-col justify-between h-40 md:h-auto">
            <div className="flex justify-between items-center mb-2">
              <span className="font-mono text-[10px] text-gray-500 uppercase">Telemetry</span>
              <Icon icon={Activity01Icon} size={14} strokeWidth={2} className="text-white" />
            </div>
            <div className="flex-grow flex items-center">
              <div className="w-full bg-white/10 h-16 rounded flex items-end px-1 gap-1">
                <div className="w-1/5 bg-accent/20 h-[40%] rounded-sm"></div>
                <div className="w-1/5 bg-accent/40 h-[60%] rounded-sm"></div>
                <div className="w-1/5 bg-accent/60 h-[30%] rounded-sm"></div>
                <div className="w-1/5 bg-accent/80 h-[80%] rounded-sm"></div>
                <div className="w-1/5 bg-accent h-[50%] rounded-sm"></div>
              </div>
            </div>
            <div className="text-right text-[10px] text-white font-mono mt-2">≤ 44GB PEAK VRAM</div>
          </div>

          <div className="md:col-span-1 md:row-span-1 glass-panel spotlight-card rounded-xl p-6 relative overflow-hidden group h-40 md:h-auto">
            <div className="absolute inset-0 bg-red-900/10 z-0"></div>
            <div className="relative z-10 flex flex-col h-full justify-between">
              <div className="flex justify-between items-start">
                <span className="font-display font-bold text-sm text-white">Claims Guard</span>
                <div className="w-2 h-2 rounded-full bg-danger animate-pulse-fast"></div>
              </div>
              <div className="font-mono text-[10px] text-red-300/70">
                <div>&gt; SCANNING COPY...</div>
                <div>&gt; 0 FORBIDDEN CLAIMS</div>
                <div>&gt; REQUIRED PHRASE: OK</div>
              </div>
            </div>
          </div>

          <div className="md:col-span-2 md:row-span-1 glass-panel spotlight-card rounded-xl p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between h-auto">
            <div className="mb-4 sm:mb-0">
              <h3 className="font-display font-bold text-xl text-white mb-2">Targeted Repair</h3>
              <p className="text-gray-300 text-xs font-mono">A failed check reruns one stage, not the campaign</p>
            </div>
            <div className="flex flex-col gap-1.5 w-full sm:w-40">
              <div className="flex justify-between text-[8px] text-gray-500 font-mono mb-1">
                <span>REGEN SCOPE</span>
                <span>1 SCENE</span>
              </div>
              <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-accent to-yellow-500 w-[33%] rounded-full"></div>
              </div>
            </div>
          </div>

          <div className="md:col-span-2 md:row-span-1 glass-panel spotlight-card rounded-xl p-6 relative overflow-hidden flex flex-col justify-center min-h-[200px] group">
            <div className="absolute inset-0">
              <img
                src="/gpu.png"
                className="w-full h-full object-cover object-[70%_35%] opacity-60 group-hover:scale-105 transition-transform duration-700"
                alt="Workstation GPU"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-black via-black/40 to-transparent"></div>
            </div>
            <div className="absolute inset-0 dot-grid opacity-30"></div>
            <div className="flex justify-between items-center mb-2 z-10 absolute top-6 left-6 right-6">
              <span className="font-display font-bold text-white text-lg">Zero Cloud</span>
              <span className="text-accent text-xs font-mono border border-accent/30 px-2 py-0.5 rounded">OFFLINE</span>
            </div>
            <div className="relative w-full h-full z-0 mt-8 opacity-60">
              <div className="absolute top-[30%] left-[20%] w-1.5 h-1.5 bg-white rounded-full animate-pulse shadow-[0_0_10px_white]"></div>
              <div className="absolute top-[40%] right-[30%] w-1 h-1 bg-gray-500 rounded-full"></div>
              <div className="absolute top-[60%] left-[40%] w-1 h-1 bg-gray-500 rounded-full"></div>
              <div className="absolute top-[25%] right-[20%] w-1.5 h-1.5 bg-white rounded-full animate-pulse delay-75 shadow-[0_0_10px_white]"></div>
              <svg className="absolute inset-0 w-full h-full" style={{ pointerEvents: 'none' }}>
                <line x1="20%" y1="30%" x2="40%" y2="60%" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5"></line>
                <line x1="20%" y1="30%" x2="80%" y2="25%" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5"></line>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
