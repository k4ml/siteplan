
import { defineConfig } from 'vite';
import { resolve } from 'path';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  // Use project root as the base to serve from all app directories
  root: resolve('.'),

  // The base URL for assets
  base: '/static/',

  plugins: [
    tailwindcss(),
  ],

  build: {
    rollupOptions: {
      input: {
        'siteplan-siteplan-app-css': resolve('src/siteplan/fe/css/app.css'),
        'siteplan-siteplan-js-main-js': resolve('src/siteplan/fe/js/main.js'),
        'siteplan-siteplan-js-page-page-js': resolve('src/siteplan/fe/js/page/page.js'),
        'django_umin-django_umin-app-css': resolve('ext-src/django-umin/src/django_umin/fe/css/app.css'),
        'django_umin-django_umin-js-main-js': resolve('ext-src/django-umin/src/django_umin/fe/js/main.js'),
        'labzero-labzero-app-css': resolve('ext-src/labzero/src/labzero/fe/css/app.css'),
        'labzero-labzero-js-main-js': resolve('ext-src/labzero/src/labzero/fe/js/main.js'),
        'labzero-labzero-js-page-page-js': resolve('ext-src/labzero/src/labzero/fe/js/page/page.js')
      }
    }
  },

  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,

    // Allow requests from any hostname (Cloudflare tunnels, ngrok, Codespaces, etc.)
    allowedHosts: ['.'],

    // Configure CORS and headers to allow all origins in development
    cors: {
      origin: '*',
      credentials: true,
    },

    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': '*',
    },

    // Configure file system access
    fs: {
      // Allow serving files from these directories
      allow: [
        resolve('.'),
        resolve('src/siteplan/fe'),
        resolve('ext-src/django-umin/src/django_umin/fe'),
        resolve('ext-src/labzero/src/labzero/fe')
      ],
      // Disable strict file system checks for proxied environments
      strict: false,
    },

    // Watch configuration to include all app fe directories
    watch: {
      // Watch these directories for changes
      include: ['src/siteplan/fe/**/*', 'ext-src/django-umin/src/django_umin/fe/**/*', 'ext-src/labzero/src/labzero/fe/**/*'],
    }
  },
});
