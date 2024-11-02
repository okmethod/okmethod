import { purgeCss } from "vite-plugin-tailwind-purgecss";
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
  publicDir: "static",
  define: {
    "process.env": process.env,
  },
  server: {
    proxy: {
      "/fastapi": {
        target: process.env.VITE_FASTAPI_PROXY_TARGET,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/fastapi/, "/api"),
      },
    },
  },
  plugins: [sveltekit(), purgeCss()],
});
