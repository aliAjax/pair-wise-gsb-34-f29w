import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 20103,
    host: "0.0.0.0",
    proxy: {
      // 本地开发同样统一走 /api，不硬编码 localhost；代理到后端容器外端口
      "/api": {
        target: "http://127.0.0.1:21103",
        changeOrigin: true
      }
    }
  }
});
