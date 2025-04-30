import { defineConfig } from 'vite';
import djuno from './djuno/vite/plugin-djuno';

export default defineConfig({
  plugins: [djuno()],
  css: {
    modules: {
      generateScopedName: '[name]_[local]_[hash:base64:5]'
    }
  },
  build: {
    outDir: 'static/vite',
    rollupOptions: {
      input: 'components/*/*.dj'
    }
  }
});
