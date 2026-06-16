import { defineConfig } from 'vite';

const isPages = process.env.NODE_ENV === 'production' && process.env.npm_lifecycle_event === 'build:pages';

export default defineConfig({
  base: isPages ? '/ars-magica/sanctum/' : '/',
  build: {
    outDir: isPages ? '../../../docs/sanctum' : 'dist',
    emptyOutDir: true,
  },
});
