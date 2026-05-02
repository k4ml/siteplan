import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { apiPlugin } from "./vite-api";

export default defineConfig({
  plugins: [react(), apiPlugin()],
  server: {
    port: 5173,
    host: "127.0.0.1",
    strictPort: true,
  },
});
