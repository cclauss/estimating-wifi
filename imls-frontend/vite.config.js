import { fileURLToPath, URL } from "url";
import process from "process";

/// <reference types="vitest" />
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";


// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue({})],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    coverage: {
      "check-coverage": true,
      reporter: ["lcovonly", "text", "text-summary", "html"],
      all: true,
      include: ["src/**/*.vue"],
      lines: 90,
      branches: 90,
      functions: 90,
    },
    reporters: "verbose",
    setupFiles: ["test/setup.js"],
  },
});
