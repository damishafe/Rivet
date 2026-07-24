import { useEffect } from 'react'

declare global {
  interface Window {
    UnicornStudio?: { init: () => void; isInitialized?: boolean }
  }
}

export function UnicornBackground() {
  useEffect(() => {
    if (window.UnicornStudio?.isInitialized) return
    if (document.querySelector('script[data-unicorn]')) return
    const script = document.createElement('script')
    script.src = '/unicornstudio.umd.js'
    script.dataset.unicorn = 'true'
    script.onload = () => {
      if (window.UnicornStudio && !window.UnicornStudio.isInitialized) {
        window.UnicornStudio.init()
        window.UnicornStudio.isInitialized = true
      }
    }
    document.head.appendChild(script)
  }, [])

  return (
    <div
      className="fixed top-0 w-full h-screen -z-10"
      style={{
        maskImage: 'linear-gradient(to bottom, transparent, black 0%, black 80%, transparent)',
        WebkitMaskImage: 'linear-gradient(to bottom, transparent, black 0%, black 80%, transparent)',
      }}
    >
      <div data-us-project-src="/hero-scene.json" className="absolute w-full h-full left-0 top-0 -z-10" />
    </div>
  )
}
