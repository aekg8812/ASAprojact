import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // ✅ 環境変数をクライアントサイドで使用可能にする
  define: {
    'process.env': process.env,
  },

  // ✅ ビルド設定
  build: {
    // 本番ビルド時に環境変数を読み込む
    minify: 'terser',
    sourcemap: false,
  },

  // ✅ 開発サーバー設定
  server: {
    port: 5173,
    strictPort: false,
    proxy: {
      // オプション: 開発時にローカルFlaskへプロキシ
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})

