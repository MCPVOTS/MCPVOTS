import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'ws'],
          components: ['./src/components/App.tsx'],
        }
      }
    }
  },
  server: {
    port: 5173,
    host: true,
    hmr: {
      port: 5174,
    },
  },
  preview: {
    port: 5173,
    host: true
  },
  css: {
    modules: {
      localsConvention: 'camelCase',
    },
  },
  define: {
    global: 'globalThis',
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
});
