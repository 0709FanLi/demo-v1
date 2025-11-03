import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
  },
  build: {
    outDir: 'build',
    sourcemap: false,
    emptyOutDir: true,
  },
  publicDir: 'public',
  // 环境变量前缀
  envPrefix: 'VITE_',
});

