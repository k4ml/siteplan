import { execSync } from "node:child_process";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { apiPlugin } from "./vite-api";

const commitSha = (() => {
  try {
    return execSync("git rev-parse --short HEAD", {
      encoding: "utf8",
    }).trim();
  } catch {
    return "dev";
  }
})();

export default defineConfig({
  plugins: [react(), apiPlugin()],
  define: {
    __MDR_VERSION__: JSON.stringify(commitSha),
  },
  server: {
    port: 5173,
    host: "127.0.0.1",
    strictPort: true,
  },
});
