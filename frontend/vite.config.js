import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl' // ✅ SSLプラグインをインポート

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    basicSsl() // ✅ プラグインを追加（これで自動的にhttpsになります）
  ],

  // ✅ ビルド設定
  build: {
    // 本番ビルド時に環境変数を読み込む
    // minify は指定しない - Viteが自動選択
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