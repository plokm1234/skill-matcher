import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages serves this as a project site at /skill-matcher/, not root —
// asset URLs need the base path or they'll 404 once deployed.
export default defineConfig({
  base: '/skill-matcher/',
  plugins: [react()],
})
