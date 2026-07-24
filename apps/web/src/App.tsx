import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Landing from '@/pages/Landing'
import Studio from '@/pages/Studio'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/studio" element={<Studio />} />
      </Routes>
    </BrowserRouter>
  )
}
