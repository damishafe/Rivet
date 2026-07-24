import { useEffect } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'

gsap.registerPlugin(ScrollTrigger)

const SCRAMBLE_CHARS = '!<>-_\\/[]{}—=+*^?#________'

class ScrambleText {
  private el: HTMLElement
  private queue: { from: string; to: string; start: number; end: number; char?: string }[] = []
  private frame = 0
  private frameRequest = 0
  private resolve: (() => void) | null = null

  constructor(el: HTMLElement) {
    this.el = el
    this.update = this.update.bind(this)
  }

  setText(newText: string) {
    const oldText = this.el.innerText
    const length = Math.max(oldText.length, newText.length)
    const promise = new Promise<void>((resolve) => (this.resolve = resolve))
    this.queue = []
    for (let i = 0; i < length; i++) {
      const from = oldText[i] || ''
      const to = newText[i] || ''
      const start = Math.floor(Math.random() * 40)
      const end = start + Math.floor(Math.random() * 40)
      this.queue.push({ from, to, start, end })
    }
    cancelAnimationFrame(this.frameRequest)
    this.frame = 0
    this.update()
    return promise
  }

  private update() {
    let output = ''
    let complete = 0
    for (const item of this.queue) {
      if (this.frame >= item.end) {
        complete++
        output += item.to
      } else if (this.frame >= item.start) {
        if (!item.char || Math.random() < 0.28) {
          item.char = SCRAMBLE_CHARS[Math.floor(Math.random() * SCRAMBLE_CHARS.length)]
        }
        output += `<span class="opacity-50">${item.char}</span>`
      } else {
        output += item.from
      }
    }
    this.el.innerHTML = output
    if (complete === this.queue.length) {
      this.resolve?.()
    } else {
      this.frameRequest = requestAnimationFrame(this.update)
      this.frame++
    }
  }
}

export function useLandingEffects() {
  useEffect(() => {
    const lenis = new Lenis({ lerp: 0.1 })
    let currentSkew = 0
    let rafId = 0
    const raf = (time: number) => {
      lenis.raf(time)
      const skewTarget = lenis.velocity * 0.1
      currentSkew += (skewTarget - currentSkew) * 0.1
      const clamped = Math.max(Math.min(currentSkew, 5), -5)
      document.querySelectorAll<HTMLElement>('.skew-target').forEach((el) => {
        el.style.transform = `skewY(${clamped}deg)`
      })
      rafId = requestAnimationFrame(raf)
    }
    rafId = requestAnimationFrame(raf)

    const onMouseMove = (e: MouseEvent) => {
      document.querySelectorAll<HTMLElement>('.spotlight-card').forEach((card) => {
        const rect = card.getBoundingClientRect()
        card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`)
        card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`)
      })
    }
    document.addEventListener('mousemove', onMouseMove)

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target as HTMLElement
            new ScrambleText(el).setText(el.innerText)
            observer.unobserve(el)
          }
        })
      },
      { threshold: 0.5 },
    )
    document.querySelectorAll('.scramble-text').forEach((el) => observer.observe(el))

    const magneticCleanups: (() => void)[] = []
    document.querySelectorAll<HTMLElement>('.btn-magnetic').forEach((btn) => {
      const onMove = (e: MouseEvent) => {
        const rect = btn.getBoundingClientRect()
        const x = e.clientX - rect.left - rect.width / 2
        const y = e.clientY - rect.top - rect.height / 2
        gsap.to(btn, { x: x * 0.3, y: y * 0.3, duration: 0.2 })
      }
      const onLeave = () => gsap.to(btn, { x: 0, y: 0, duration: 0.2 })
      btn.addEventListener('mousemove', onMove)
      btn.addEventListener('mouseleave', onLeave)
      magneticCleanups.push(() => {
        btn.removeEventListener('mousemove', onMove)
        btn.removeEventListener('mouseleave', onLeave)
      })
    })

    const ctx = gsap.context(() => {
      const counter = document.querySelector<HTMLElement>('.counter')
      if (counter) {
        const target = Number(counter.dataset.target || '0')
        const state = { value: 0 }
        gsap.to(state, {
          value: target,
          duration: 2,
          ease: 'power1.out',
          scrollTrigger: { trigger: counter, start: 'top 85%', once: true },
          onUpdate: () => {
            counter.textContent = String(Math.round(state.value))
          },
        })
      }

      document.querySelectorAll<HTMLElement>('.step-item').forEach((item) => {
        ScrollTrigger.create({
          trigger: item,
          start: 'top 80%',
          end: 'bottom center',
          onEnter: () => gsap.to(item, { opacity: 1, duration: 0.5 }),
          onLeave: () => gsap.to(item, { opacity: 0.3, duration: 0.5 }),
          onEnterBack: () => gsap.to(item, { opacity: 1, duration: 0.5 }),
          onLeaveBack: () => gsap.to(item, { opacity: 0.3, duration: 0.5 }),
        })
      })

      gsap.utils.toArray<HTMLElement>('.glass-panel').forEach((panel, i) => {
        gsap.from(panel, {
          scrollTrigger: { trigger: panel, start: 'top 90%' },
          y: 30,
          opacity: 0,
          duration: 0.8,
          delay: i * 0.05,
          ease: 'power3.out',
        })
      })
    })

    return () => {
      cancelAnimationFrame(rafId)
      lenis.destroy()
      document.removeEventListener('mousemove', onMouseMove)
      observer.disconnect()
      magneticCleanups.forEach((fn) => fn())
      ctx.revert()
      document.querySelectorAll<HTMLElement>('.skew-target').forEach((el) => {
        el.style.transform = ''
      })
    }
  }, [])
}
