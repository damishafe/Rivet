import { Link } from 'react-router-dom'
import { GithubIcon } from '@hugeicons/core-free-icons'
import { Icon } from '@/components/icons/Icon'

export function Footer() {
  return (
    <footer className="bg-[#020202] pt-32 pb-10 px-6 border-t border-white/10 relative overflow-hidden">
      <div className="absolute bottom-0 left-0 w-full select-none pointer-events-none opacity-5 leading-none">
        <svg className="block w-full" viewBox="0 0 740 190" aria-hidden="true">
          <text
            x="0"
            y="188"
            fontSize="258"
            fontWeight="700"
            fill="#ffffff"
            textLength="740"
            lengthAdjust="spacingAndGlyphs"
            style={{ fontFamily: '"Space Grotesk", sans-serif' }}
          >
            RIVET
          </text>
        </svg>
      </div>

      <div className="max-w-[1400px] mx-auto relative z-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-12">
        <div>
          <h3 className="text-2xl font-display font-bold text-white mb-6">Ready to verify?</h3>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              to="/studio"
              className="bg-accent text-black px-6 py-3 rounded font-bold text-sm hover:bg-white transition-colors text-center"
            >
              OPEN STUDIO
            </Link>
            <a
              href="https://github.com/damishafe/Rivet"
              className="flex items-center justify-center gap-2 border border-white/10 bg-white/5 px-6 py-3 rounded font-bold text-sm text-white hover:border-accent transition-colors"
            >
              <Icon icon={GithubIcon} size={16} strokeWidth={2} /> GITHUB
            </a>
          </div>
        </div>

        <div className="flex gap-12 text-sm text-gray-500 font-mono tracking-wider uppercase">
          <div className="flex flex-col gap-3">
            <span className="text-white">Product</span>
            <Link to="/studio" className="hover:text-accent transition-colors">Studio</Link>
            <a href="#pipeline" className="hover:text-accent transition-colors">Pipeline</a>
            <a href="#guarantees" className="hover:text-accent transition-colors">Guarantees</a>
          </div>
          <div className="flex flex-col gap-3">
            <span className="text-white">Project</span>
            <a href="https://github.com/damishafe/Rivet" className="hover:text-accent transition-colors">License</a>
            <a href="https://github.com/damishafe/Rivet" className="hover:text-accent transition-colors">Models</a>
          </div>
        </div>
      </div>

      <div className="max-w-[1400px] mx-auto mt-20 pt-6 border-t border-white/5 flex flex-col md:flex-row justify-between items-center text-[10px] text-gray-600 font-mono uppercase gap-4 md:gap-0">
        <span>© 2026 RIVET</span>
        <span className="md:mt-0">BUILT LOCAL · ROCm 7.2.1 · RADEON PRO W7900</span>
      </div>
    </footer>
  )
}
