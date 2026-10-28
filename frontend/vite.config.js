import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api/finance': {
        target: 'http://localhost:8001',
        rewrite: (path) => path.replace(/^\/api\/finance/, ''),
        changeOrigin: true,
      },
      '/api/registration': {
        target: 'http://localhost:8002',
        rewrite: (path) => path.replace(/^\/api\/registration/, ''),
        changeOrigin: true,
      },
      '/api/learning': {
        target: 'http://localhost:8003',
        rewrite: (path) => path.replace(/^\/api\/learning/, ''),
        changeOrigin: true,
      },
      '/api/zenkai': {
        target: 'http://localhost:8004',
        rewrite: (path) => path.replace(/^\/api\/zenkai/, ''),
        changeOrigin: true,
      },
    },
  },
})
