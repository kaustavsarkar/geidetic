import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ["pdfjs-dist"], // optionally specify dependency name
    esbuildOptions: {
      supported: {
        "top-level-await": true
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        dir: 'ain/frontend/dist'
      }
    }
  }
})
