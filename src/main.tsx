import "@fontsource/ibm-plex-mono/400.css"
import "@fontsource/ibm-plex-mono/500.css"
import "@fontsource-variable/ibm-plex-sans/wght.css"
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { MotionConfig } from "motion/react"

import App from "./App"
import "./index.css"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <MotionConfig reducedMotion="user">
      <App />
    </MotionConfig>
  </StrictMode>,
)
