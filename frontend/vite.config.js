// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // This makes the server accessible from outside the container
    port: 5173,
    watch: {
      usePolling: true, // Needed for Docker to detect file changes
    },
  },
})