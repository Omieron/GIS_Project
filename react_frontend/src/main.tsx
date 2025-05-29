import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import MapInitializer from './components/map/MapInitializer'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MapInitializer />
  </StrictMode>
)