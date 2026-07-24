import { UnicornBackground } from '@/components/landing/UnicornBackground'
import { Nav } from '@/components/landing/Nav'
import { Hero } from '@/components/landing/Hero'
import { Marquee } from '@/components/landing/Marquee'
import { Bento } from '@/components/landing/Bento'
import { Cli } from '@/components/landing/Cli'
import { Pipeline } from '@/components/landing/Pipeline'
import { CampaignPack } from '@/components/landing/CampaignPack'
import { Footer } from '@/components/landing/Footer'
import { useLandingEffects } from '@/components/landing/useLandingEffects'

export default function Landing() {
  useLandingEffects()

  return (
    <>
      <div className="fixed inset-0 bg-[#050505] -z-50"></div>
      <UnicornBackground />
      <div className="noise-overlay"></div>
      <Nav />
      <main>
        <Hero />
        <Marquee />
        <Bento />
        <Cli />
        <Pipeline />
        <CampaignPack />
        <Footer />
      </main>
    </>
  )
}
