import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './styles/MapInitializer.css'
import MapInitializer from './components/map/MapInitializer.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MapInitializer />
  </StrictMode>,
)
